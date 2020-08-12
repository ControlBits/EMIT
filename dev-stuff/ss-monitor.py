#
# ss-monitor.py  = Super Simple MQTT monitor to help with IoT development
# written by Jon Luke @ ControlBits.com
# 12 August 2020
#


# import required modules
import paho.mqtt.client as mqtt
import threading
import http.client, urllib

# set up variables
mqtt_broker = 'public.mqtthq.com'
topic = '1116fa09-973c-4fa3-aff1-3f9859c819bd'

alarm_period = 20 # in seconds - suggest this is > 3 missed message at normal transmission frequency
alarm_count = 0
alarm_triggered = 0


# define call back functions
def on_connect(client, userdata, flags, rc):
    print("Connection successful!")

    print("Subscribing to topic: ", topic)
    client.subscribe(topic, qos=0)
    print("Subscription successful!")

    # start alarm timer
    check_now(alarm_check)
    print("Timer started ...")


def on_message(client, userdata, message):

    global alarm_count, alarm_triggered

    # print("Message received! -> resetting alarm counter")
    print("Time since last message = " + str(alarm_count) + " seconds")

    # reset alarm count & trigger
    alarm_count = 0
    alarm_triggered = 0


def check_now(alarm_check):

    global alarm_count, alarm_triggered

    alarm_count = alarm_count + 1
    # print("Alarm count = " + str(alarm_count))

    if alarm_count == alarm_period and alarm_triggered == 0:
        alarm_count = 0 # reset counter
        alarm_triggered = 1
        print("ALARM: No message received for " + str(alarm_period) + " seconds!")

        # send ALARM message via Pushover
        conn = http.client.HTTPSConnection("api.pushover.net:443")

        conn.request("POST", "/1/messages.json",
          urllib.parse.urlencode({
            "token":"replace-with-your-pushover-token",
            "user":"replace-with-your-pushover-user-id",
            "message":"ALARM: No message received for " + str(alarm_period) + " seconds! (python monitor)"
          }), { "Content-type": "application/x-www-form-urlencoded" })

        conn.getresponse()


    if alarm_check.is_set(): # restart the timer
        threading.Timer(1, check_now, [alarm_check]).start()




# Create MQTT client
client = mqtt.Client()

# Create alarm_check thread to check for alarm condition every second
alarm_check = threading.Event()
alarm_check.set()

# Define callback function for successful connection
client.on_connect = on_connect

# Define callback function for receipt of a message
client.on_message = on_message

# Connect to broker
print("Connecting to broker: ", mqtt_broker)
client.connect(mqtt_broker)

# Loop indefinately ... callback functions will drive actions
client.loop_forever()
