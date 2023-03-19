from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models import Q
from django.core import serializers

# Implements observer-like functionalities
from django.db.models.signals import post_save
from django.dispatch import receiver
from time import sleep


# Create your models here.

class CustomUser(AbstractUser):
    firstName = models.CharField(max_length = 40)
    lastName = models.CharField(max_length = 40)
    isClient = models.BooleanField('client status', default = False)
    isDriver = models.BooleanField('driver status', default = False)
    lat = models.FloatField(verbose_name = 'lat', default = 0.0)
    lng = models.FloatField(verbose_name = 'lng', default = 0.0)

class Driver(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    carModel = models.CharField(max_length = 30)
    registrationNumber = models.CharField(max_length = 30)
    numberOfReviews = models.IntegerField(default = 0)
    grade = models.FloatField(default = 0.0)

    def __str__(self):
        return "{}".format(self.driver)

class Trip(models.Model):

    NEUTRAL = -1
    CANCELED = 0
    PLACED = 1
    DRIVER_ON_THE_WAY = 2
    TRANSIT = 3
    REVIEW = 4
    FINISHED = 5

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='rider_id', null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, verbose_name='driver_id', null=True, blank=True)
    destination = models.CharField(verbose_name = 'destination', max_length=80)
    latClient = models.FloatField(verbose_name = 'lat_client', default = 0.0)
    lngClient = models.FloatField(verbose_name= 'lng_client', default = 0.0)
    latDestination = models.FloatField(verbose_name = 'lat_destination', default = 0.0)
    lngDestination = models.FloatField(verbose_name = 'lng_destination', default = 0.0)
    tripTime = models.DateTimeField(verbose_name='trip_time', auto_now_add=True)
    details = models.CharField(verbose_name='details', max_length = 200)
    status = models.IntegerField(verbose_name='status', default = -1)

@receiver(post_save, sender=Trip)
def observer_notify_client_on_status_change(sender, instance, **kwargs):

    if instance.status == Trip.DRIVER_ON_THE_WAY:
        message = ChatMessage.objects.create(
            messageSender = instance.driver.driver,
            messageReceiver = instance.rider,
            tripReference = instance,
            messageStatus = ChatMessage.PENDING,
            messageData = "YOUR TRIP HAS BEEN ACCEPTED BY A DRIVER"
        )

class ChatMessage(models.Model):

    PENDING = 0
    LISTED = 1

    messageSender = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='message_sender', related_name='message_sender', null=True, blank=True)
    messageReceiver = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='message_receiver', null=True, blank=True)
    tripReference = models.ForeignKey(Trip, on_delete=models.PROTECT, verbose_name='trip_reference', null=True, blank=True)
    messageStatus = models.IntegerField(verbose_name='message_status', default = 0)
    messageData = models.CharField(verbose_name='message_data', max_length=200)



def getUserByUsername(user):
    try:
        ret = CustomUser.objects.get(username=user)
    except CustomUser.DoesNotExist:
        return None
    
    return ret

def getActiveTripForUser(rider):
    try:
        ret = Trip.objects.get(Q(rider = rider) & 
        (Q(status = Trip.PLACED) | Q(status = Trip.DRIVER_ON_THE_WAY) | Q(status = Trip.TRANSIT) 
        |Q(status = Trip.REVIEW)))
    except:
        ret = None

    return ret

def getPlacedTripForUser(rider):
    try:
        ret = Trip.objects.get(Q(rider = rider) & 
        Q(status = Trip.PLACED))
    except:
        ret = None

    return ret

def getTranzitTripForUser(rider):
    try:
        ret = Trip.objects.get(Q(rider = rider) & 
        Q(status = Trip.TRANSIT))
    except:
        ret = None

    return ret

def getAcceptedTripForUser(rider):
    try:
        ret = Trip.objects.get(Q(rider = rider) & 
        (Q(status = Trip.DRIVER_ON_THE_WAY) | Q(status = Trip.TRANSIT) 
        |Q(status = Trip.REVIEW)))
    except:
        ret = None
    
    return ret

def getDriverByUsername(username):
    try:
        user = CustomUser.objects.get(username = username)
        ret = Driver.objects.get(driver = user)
    except:
        ret = None
    
    return ret

def getPendingTripForUser(rider):
    try:
        ret = Trip.objects.get(Q(rider = rider) & 
        Q(status = Trip.PLACED))
    except:
        ret = None

    return ret

def getActiveTripForDriver(driver):
    try:
        ret = Trip.objects.get(Q(driver = driver) & 
        (Q(status = Trip.DRIVER_ON_THE_WAY) | Q(status = Trip.TRANSIT) 
        |Q(status = Trip.REVIEW)))
    except:
        ret = None

    return ret

def getOnTheWayTripForDriver(driver):
    try:
         ret = Trip.objects.get(Q(driver = driver) & 
        Q(status = Trip.DRIVER_ON_THE_WAY))
    except:
        ret = None
    
    return ret

def setTripToTranzit(trip):
    trip.status = Trip.TRANSIT
    trip.save()

def setTripToReview(trip):
    trip.status = Trip.REVIEW
    trip.save()

def setTripToFinished(trip):
    trip.status = Trip.FINISHED
    trip.save()

def addTrip(username, destination, latClient, lngClient, latDestination, lngDestination, details):
    rider = getUserByUsername(username)
    Trip.objects.create(rider = rider, destination = destination, 
    latClient = latClient,
    lngClient = lngClient,
    latDestination = latDestination,
    lngDestination = lngDestination,
    details = details, 
    status = Trip.PLACED)

# Treaba asta nu o sa functioneze doar daca imi creez un camp in baza de date care specifica daca user ul este conecatat sau nu. Pana atunci ne facem ca problema nu exista.
def isUserLoggedIn(username):
    try:
        user = CustomUser.objects.get(username = username)
        return user.is_authenticated
    except:
        return False

def getDriverForUser(user):
    try:
        ret = Driver.objects.get(driver = user)
    except:
        ret = None
    
    return ret

def getAvailableDrivers():
    driversUsers = CustomUser.objects.filter(isDriver = True)
    ret = []
    for x in driversUsers:
        driver = getDriverForUser(x)
        if getActiveTripForDriver(driver) == None and isUserLoggedIn(x.username):
            ret.append(driver)

    return ret

def isRiderPending(user):
    try:
        ret = Trip.objects.get(Q(rider = user) & Q(status = Trip.PLACED))
    except:
        ret = None
    return ret

def getRidersLookingForTrip():
    riderUsers = CustomUser.objects.filter(isClient = True)
    ret = []
    for x in riderUsers:
        if (isRiderPending(x) is not None):
            ret.append(serializers.serialize('json', [x]))
            #print (serializers.serialize('json', [x]))

    #print (ret)
    return ret

def getPlacedTrips():
    try:
        aux = Trip.objects.filter(status = Trip.PLACED)
        ret = serializers.serialize('json', aux)
    except:
        ret = None
    
    return ret

def acceptTrip(pk, username):
    try:

        trip = Trip.objects.get(Q(pk = pk) & Q(status = Trip.PLACED))
        driver = getDriverByUsername(username)
        trip.driver = driver
        trip.status = Trip.DRIVER_ON_THE_WAY
        trip.save()
        ret = True

    except:
        ret = False
    
    return ret

def getDriverForTrip(trip):
    try:
        aux = trip.driver_id
        ret = Driver.objects.get(pk = aux)
    except:
        ret = None
    
    return ret

def getUserForDriver(driver):
    try:
        ret = driver.driver
    except:
        ret = None
    
    return ret

def getUserForTrip(trip):
    try:
        aux = trip.rider_id
        ret = CustomUser.objects.get(pk = aux)
    except:
        ret = None

    return ret

def addChatMessage(sender, receiver, trip, message):
    try:
        ChatMessage.objects.create(messageSender = sender, messageReceiver = receiver, tripReference = trip, messageData = message, messageStatus = ChatMessage.PENDING)
    except:
        return None

def getPendingMessageForUser(user, trip):
    try:
        aux = ChatMessage.objects.filter(Q(messageReceiver = user) & Q(tripReference = trip) & Q(messageStatus = ChatMessage.PENDING))
        ret = aux[0]
        ret.messageStatus = ChatMessage.LISTED
        ret.save()
        return ret
    
    except:
        return None

def updateDriverRating(driver, review):
    aux = (driver.numberOfReviews * driver.grade + review) / (driver.numberOfReviews + 1)
    driver.grade = aux
    driver.numberOfReviews += 1
    driver.save()