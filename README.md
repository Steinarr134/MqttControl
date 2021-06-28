


# MqttControl

This is project is all about a Class called Communicatable which other classes can inherit and it allows for very easy set up of control through mqtt.

Best to look at an example: 
  
	class Example(Communicatable):  
	    def __init__(self, mqtt, something=0):  
	        Communicatable.__init__(self, mqtt, "example")   # 'example' is the control name
	        self.something = something  
	        self.mqtt_settable("something")  
	        self.mqtt_callable("foo")  
	  
	    def foo(self, input1, input2, optional1=None, optional2=None):  
	        self.something = input1 + input2  
	        print(f"{optional1=}, {optional2=}")  
	          

Example inherits the Communicatable class and the simple line self.mqtt_Settable("something") is all that is needed for self.something to be both settable and gettable through mqtt.

Here is an example of how to initialize our `Example()` class:

	from paho.mqtt.client import Client as MqttClient  
	client = MqttClient("Test")  
	client.connect("localhost")  
	client.loop_start()
	
	example = Example(client)

Now `example.something` can be controlled by connecting to the same mqtt server and posting to `example/set`:

    client.publish("example/set", json.dumps({"something": 15}))
    client.publish("example/call", json.dumps(["foo", [1, 2], {"optional1": "hello", "optional2": "dis working?"}]))
