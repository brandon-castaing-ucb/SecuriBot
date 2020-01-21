import paho.mqtt.client as mqtt


def tx2_connect(client, userdata, flags, rc):
    print("Connected to the TX2 MQTT with result code: " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("faces/us")
    client.subscribe("faces/unknown")


def cloud_connect(client, userdata, flags, rc):
    print("Connected to the cloud MQTT with result code: " + str(rc))

    #Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("faces/us")
    client.subscribe("faces/unknown")


def tx2_message(client, userdata, msg):
    print("Message received on " + msg.topic)
    print("Publishing message to the cloud...")
    cloud_client.publish(msg.topic, msg.payload)
    
def cloud_publish(client, userdata, result):
    print("Message published: " + str(result))


tx2_client = mqtt.Client()
tx2_client.on_connect = tx2_connect
tx2_client.on_message = tx2_message
tx2_client.connect("mosquitto", 1883, 60)

cloud_client = mqtt.Client()
cloud_client.on_connect = cloud_connect
cloud_client.on_publish = cloud_publish
cloud_client.connect("169.55.53.164", 1883, 60)

tx2_client.loop_forever()
