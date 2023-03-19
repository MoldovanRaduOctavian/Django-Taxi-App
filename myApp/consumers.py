import json
from channels.generic.websocket import WebsocketConsumer, AsyncConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from . import models
from django.core import serializers


class ChatConsumer(AsyncConsumer):
    
    async def websocket_connect(self, event):
        
        await self.send({
            'type': 'websocket.accept'
        })
        # await self.send({
        #     'type': 'websocket.send',
        #     'text': 'TEST'
        # })

    async def websocket_disconnect(self, event):
        print("E decent")
        

    async def websocket_receive(self, event):
        # print('received')
        # await self.send({
        #     'type': 'websocket.send',
        #     'text': 'Ai trimis asta: ' + event["text"]
        # })

        message = json.loads(event['text'])

        if message["type"] == 'find_rider':
            aux = await self.getUserByUsername(message["username"])
            data = "L-am gasit!"
            if aux == None:
                data = "Nu exista!"

            await self.send({
                'type': 'websocket.send',
                'text': data
            })
        

        # ws.send(JSON.stringify({
        #         "type": "place_order",
        #         "clientLat": clientLat,
        #         "clientLng": clientLng,
        #         "tripDestination": tripDestination,
        #         "tripDetails": tripDetails,
        #         "destinationLat": destinationLat,
        #         "destinationLng": destinationLng,
        #     }));
        
        elif message["type"] == "place_order":
            rider = await self.getUserByUsername(message["user"])
            username = message["user"]
            clientLat = message["clientLat"]
            clientLng = message["clientLng"]
            tripDestination = message["tripDestination"]
            tripDetails = message["tripDetails"]
            destinationLat = message["destinationLat"]
            destinationLng = message["destinationLng"]

            if (await self.getActiveTripForUser(rider) == None):
                await self.addTrip(username, tripDestination, clientLat, clientLng, destinationLat, destinationLng, tripDetails)
                await self.send({
                    'type': "websocket.send",
                    'text': "{\"type\": \"place_trip_status\", \"message\": true}"
                })
            else:
                await self.send({
                    'type': "websocket.send",
                    'text': "{\"type\": \"place_trip_status\", \"message\": false}"
                })

        elif message["type"] == "check_active_ride":
            rider = await self.getUserByUsername(message["user"])
            placedTrip = await self.getPlacedTripForUser(rider)
            if (placedTrip == None):
                retDict = {
                    'type': "cancel_button_enable",
                    'status': False,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
            else:
                # await self.send({
                #     'type': "websocket.send",
                #     'text': "{ \"type\": \"cancel_button_enable\", \"data\": true}"
                # })

                tripData = {
                    'tripDestination': placedTrip.destination,
                    'tripDetails': placedTrip.details,
                }

                retDict = {
                    'type': "cancel_button_enable",
                    'status': True,
                    'data': tripData
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })

        elif message["type"] == "cancel_trip":
            rider = await self.getUserByUsername(message["user"])
            trip = await self.getActiveTripForUser(rider)
            if (trip is not None):
                await self.cancelTrip(trip)

        elif message["type"] == "update_position":
            user = await self.getUserByUsername(message["user"])
            clientLat = message['clientLat']
            clientLng = message['clientLng']
            await self.updatePositionForUser(user, clientLat, clientLng)

        elif message["type"] == "look_for_pending_clients":
            ridersPending = await self.getRidersLookingForTrip()
            retDict = {'type' : 'found_pending_clients',
                        'data': ridersPending,
                        }
            json_string = json.dumps(retDict)

            await self.send({
                'type': "websocket.send",
                'text': json_string,
            })
        
        elif message["type"] == "look_for_placed_trips":
            placedTrips = await self.getPlacedTrips()
            retDict = {
                'type': 'found_placed_trips',
                'data': placedTrips,
            }
            json_string = json.dumps(retDict)

            await self.send({
                'type': "websocket.send",
                'text': json_string,
            })
        
        elif message["type"] == "try_accept_ride":
            acceptStatus = await self.acceptTrip(message["ride-pk"], message["user"])
            retDict = {
                'type': 'accept_ride_status',
                'data': acceptStatus,
            }
            json_string = json.dumps(retDict)

            await self.send({
                'type': "websocket.send",
                'text': json_string,
            })

        elif message["type"] == "check_accepted_ride":
            rider = await self.getUserByUsername(message["user"])
            acceptedTrip = await self.getAcceptedTripForUser(rider)

            if (acceptedTrip != None):
                #print(acceptedTrip.driver_id)
                driver = await self.getDriverForTrip(acceptedTrip)
                driverUser = await self.getUserForDriver(driver)

                driverData = {
                    'driverCar': driver.carModel,
                    'driverRegistration': driver.registrationNumber,
                    'driverNumReviews': driver.numberOfReviews,
                    'driverGrade': driver.grade,
                    'driverFirstName': driverUser.firstName,
                    'driverLastName': driverUser.lastName,
                    'tripDestination': acceptedTrip.destination,
                    'tripDetails': acceptedTrip.details,
                }

                retDict = {
                    'type': 'send_accepted_ride',
                    'status': True,
                    'data': driverData,
                }
                
                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })

            else:
                retDict = {
                    'type': 'send_accepted_ride',
                    'status': False,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string
                })
        elif message["type"] == "check_driver_on_the_way":
            driver = await self.getDriverByUsername(message["user"])
            onTheWayTrip = await self.getOnTheWayTripForDriver(driver)

            if (onTheWayTrip != None):
                
                onTheWayTripData = {
                    'tripDestination': onTheWayTrip.destination,
                    'tripDetails': onTheWayTrip.details,
                }

                retDict = {
                    'type': 'cancel_button_enable_driver',
                    'status': True,
                    'data': onTheWayTripData
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string
                })

            else:
                retDict = {
                    'type': 'cancel_button_enable_driver',
                    'status': False
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
        
        elif message["type"] == "cancel_trip_driver":
            driver = await self.getDriverByUsername(message["user"])
            onTheWayTrip = await self.getOnTheWayTripForDriver(driver)

            if (onTheWayTrip != None):
                await self.cancelTrip(onTheWayTrip)

        elif message["type"] == "tranzit_trip_driver":
            driver = await self.getDriverByUsername(message["user"])
            onTheWayTrip = await self.getOnTheWayTripForDriver(driver)

            if (onTheWayTrip != None):
                await self.setTripToTranzit(onTheWayTrip)
        
        elif message["type"] == "check_tranzit_ride":
            rider = await self.getUserByUsername(message["user"])
            tranzitTrip = await self.getTranzitTripForUser(rider)

            if (tranzitTrip != None):
                retDict = {
                    'type': 'send_tranzit_ride',
                    'status': True,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })

            else:

                retDict = {
                    'type': 'send_tranzit_ride',
                    'status': False,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
        
        # elif message["type"] == "send_chat_message_rider":
        #     rider = await self.getUserByUsername(message["user"])
        #     acceptedTrip = await self.getAcceptedTripForUser(rider)

        #     if (acceptedTrip != None):
        #         driver = await self.getDriverForTrip(acceptedTrip)
        #         userDriver = await self.getUserForDriver(driver)

        #         retDict = {
        #             'type': 'response_chat_message_rider',
        #             'chatMessage': message["chat-message"],
        #             'receiver': userDriver.username
        #         }

        #         json_string = json.dumps(retDict)

        #         await self.send({
        #             'type': "websocket.send",
        #             'text': json_string,
        #         })
        
        elif message["type"] == "send_chat_message_rider":
            rider = await self.getUserByUsername(message["user"])
            acceptedTrip = await self.getAcceptedTripForUser(rider)

            if (acceptedTrip != None):
                driver = await self.getDriverForTrip(acceptedTrip)
                userDriver = await self.getUserForDriver(driver)

                await self.addChatMessage(rider, userDriver, acceptedTrip, message["chat-message"])

        # elif message["type"] == "send_chat_message_driver":
        #     driver = await self.getDriverByUsername(message["user"])
        #     activeTrip = await self.getActiveTripForDriver(driver)

        #     if (activeTrip != None):
        #         print("Aloooooo")
        #         rider = await self.getUserForTrip(activeTrip)

        #         retDict = {
        #             'type': 'response_chat_message_driver',
        #             'chatMessage': message["chat-message"],
        #             'receiver': rider.username,
        #         }

        #         json_string = json.dumps(retDict)

        #         await self.send({
        #             'type': "websocket.send",
        #             'text': json_string,
        #         })

        elif message["type"] == "send_chat_message_driver":
            driverSenderUser = await self.getUserByUsername(message["user"])
            driverReference = await self.getDriverByUsername(message["user"])
            activeTrip = await self.getActiveTripForDriver(driverReference)

            if (activeTrip != None):
                rider = await self.getUserForTrip(activeTrip)
                chatMessageData = message["chat-message"]

                await self.addChatMessage(driverSenderUser, rider, activeTrip, chatMessageData)

        elif message["type"] == "check_driver_active":
            driver = await self.getDriverByUsername(message["user"])
            activeTrip = await self.getActiveTripForDriver(driver)
            
            if (activeTrip != None):
                
                
                retDict = {
                    'type': 'chat_enable_driver',
                    'status': True,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string
                })

            else:
                retDict = {
                    'type': 'chat_enable_driver',
                    'status': False
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })

        elif message["type"] == "poll_for_message_driver":
            driver = await self.getDriverByUsername(message["user"])
            driverUser = await self.getUserForDriver(driver)
            activeTrip = await self.getActiveTripForDriver(driver)

            if (activeTrip != None):
                pendingMessage = await self.getPendingMessagesForUser(driverUser, activeTrip)

                if (pendingMessage != None):
                    
                    messageData =  pendingMessage.messageData

                    retDict = {
                        'type': 'pending_message_for_driver',
                        'messageData': messageData,
                    }

                    json_string = json.dumps(retDict)

                    await self.send({
                        'type': "websocket.send",
                        'text': json_string,
                    })

        elif message["type"] == "poll_for_message_rider":
            rider = await self.getUserByUsername(message["user"])
            acceptedTrip = await self.getAcceptedTripForUser(rider)

            if (acceptedTrip != None):
                pendingMessage = await self.getPendingMessagesForUser(rider, acceptedTrip)

                

                if (pendingMessage != None):

                    messageData = pendingMessage.messageData

                    retDict = {
                        'type': 'pending_message_for_rider',
                        'messageData': messageData, 
                    }

                    json_string = json.dumps(retDict)

                    await self.send({
                        'type': "websocket.send",
                        'text': json_string,
                    })

        elif message["type"] == "destination_trip_driver":
            driver = await self.getDriverByUsername(message["user"])
            activeTrip = await self.getActiveTripForDriver(driver)

            print ("Debug print")

            if (activeTrip != None):
                await self.setTripToReview(activeTrip)

        elif message["type"] == "check_driver_tranzit":
            driver = await self.getDriverByUsername(message["user"])
            acceptedTrip = await self.getActiveTripForDriver(driver)

            if (acceptedTrip != None and acceptedTrip.status == models.Trip.TRANSIT):
                
                retDict = {
                    'type': 'destination_button_enable_driver',
                    'status': True,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
            
            else:

                retDict = {
                    'type': 'destination_button_enable_driver',
                    'status': False,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })

        elif message["type"] == "check_review_ride":
            rider = await self.getUserByUsername(message["user"])
            acceptedTrip = await self.getAcceptedTripForUser(rider)

            if (acceptedTrip != None and acceptedTrip.status == models.Trip.REVIEW):

                retDict = {
                    'type': 'send_review_ride',
                    'status': True,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
            
            else:

                retDict = {
                    'type': 'send_review_ride',
                    'status': False,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
        
        elif message["type"] == "review_trip_rider":
            rider = await self.getUserByUsername(message["user"])
            acceptedTrip = await self.getAcceptedTripForUser(rider)

            if (acceptedTrip != None and acceptedTrip.status == models.Trip.REVIEW):
                driver = await self.getDriverForTrip(acceptedTrip)

                await self.updateDriverRating(driver, message["rating"])
                await self.setTripToFinished(acceptedTrip)
            

        elif message["type"] == "check_driver_review":
            driver = await self.getDriverByUsername(message["user"])
            activeTrip = await self.getActiveTripForDriver(driver)

            

            if (activeTrip != None and activeTrip.status == models.Trip.REVIEW):

                retDict = {
                    'type': 'send_review_trip_driver',
                    'status': True,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })
            
            else:

                retDict = {
                    'type': 'send_review_trip_driver',
                    'status': False,
                }

                json_string = json.dumps(retDict)

                await self.send({
                    'type': "websocket.send",
                    'text': json_string,
                })


    @database_sync_to_async
    def getUserByUsername(self, user):
        return models.getUserByUsername(user)

    @database_sync_to_async
    def getActiveTripForUser(self, rider):
        return models.getActiveTripForUser(rider)

    @database_sync_to_async
    def getActiveTripForDriver(self, driver):
        return models.getActiveTripForDriver(driver)

    @database_sync_to_async
    def getPlacedTripForUser(self, rider):
        return models.getPlacedTripForUser(rider)

    @database_sync_to_async
    def addTrip(self, username, destination, latClient, lngClient, latDestination, lngDestination, details):
        models.addTrip(username, destination, latClient, lngClient, latDestination, lngDestination, details)
    
    @database_sync_to_async
    def cancelTrip(self, trip):
        trip.status = models.Trip.CANCELED
        trip.save()
    # async def chat_message(self, event):
    #     message = event['message']

    #     await self.send(text_data=json.dumps({"message": "Ti-am trimis asta: " + message}))

    @database_sync_to_async
    def getAvailableDrivers(self):
        return models.getAvailableDrivers()

    @database_sync_to_async
    def updatePositionForUser(self, user, lat, lng):
        if user is not None:
            user.lat = lat
            user.lng = lng
            user.save()
    
    @database_sync_to_async
    def getRidersLookingForTrip(self):
        return models.getRidersLookingForTrip()

    @database_sync_to_async
    def getPlacedTrips(self):
        return models.getPlacedTrips()
    
    @database_sync_to_async
    def acceptTrip(self, pk, username):
        return models.acceptTrip(pk, username)

    @database_sync_to_async
    def getAcceptedTripForUser(self, rider):
        return models.getAcceptedTripForUser(rider)
    
    @database_sync_to_async
    def getDriverForTrip(self, trip):
        return models.getDriverForTrip(trip)

    @database_sync_to_async
    def getUserForDriver(self, driver):
        return models.getUserForDriver(driver)
    
    @database_sync_to_async
    def getDriverByUsername(self, username):
        return models.getDriverByUsername(username)

    @database_sync_to_async
    def getOnTheWayTripForDriver(self, driver):
        return models.getOnTheWayTripForDriver(driver)
    
    @database_sync_to_async
    def setTripToTranzit(self, trip):
        return models.setTripToTranzit(trip)

    @database_sync_to_async
    def getTranzitTripForUser(self, rider):
        return models.getTranzitTripForUser(rider)

    @database_sync_to_async
    def getUserForTrip(self, trip):
        return models.getUserForTrip(trip)
    
    @database_sync_to_async
    def addChatMessage(self, sender, receiver, trip, message):
        return models.addChatMessage(sender, receiver, trip, message)
    
    @database_sync_to_async
    def getPendingMessagesForUser(self, user, trip):
        return models.getPendingMessageForUser(user, trip)

    @database_sync_to_async
    def setTripToReview(self, trip):
        return models.setTripToReview(trip)

    @database_sync_to_async
    def setTripToFinished(self, trip):
        return models.setTripToFinished(trip)

    @database_sync_to_async
    def updateDriverRating(self, driver, review):
        return models.updateDriverRating(driver, review)