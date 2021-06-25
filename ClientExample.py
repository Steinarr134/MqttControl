from Client import *

if __name__ == '__main__':
    import time
    from paho.mqtt.client import Client
    c = Client("Test")
    c.on_message = lambda a, b, m: print("Unfiltered Message!! : ", m)
    c.connect("localhost")
    c.loop_start()


    class Example(Communicatable):
        def __init__(self, mqtt, something):
            Communicatable.__init__(self, mqtt, "comtest")
            self.something = something
            self.mqtt_settable("something")
            self.mqtt_callable("foo")

        def foo(self, input1, input2, optional1=None, optional2=None):
            self.something = input1 + input2
            print(f"{optional1=}, {optional2=}")

        #   This is enough for the 'something' to be automatically gotten and set but below is how to implement a setter
        #   to react when things get set

        @property
        def something(self):
            return self.__something

        @something.setter
        def something(self, val):
            print("from setter: something was set to {}".format(val))
            self.__something = val


    print("initializing example class with something = 10")
    example = Example(c, 10)

    print("at this time: example.something =", example.something, "\n")

    print("manually changing example.something")
    example.something = 12.5

    print("at this time: example.something =", example.something, "\n")

    print("publishing on comtest/set")
    c.publish("comtest/set", json.dumps({"something": 15}))
    time.sleep(0.1)  # allow time for message to arrive

    print("in the end: example.something =", example.something)

    # run heartbeat for a while

    print("now for calling")

    c.publish("comtest/call", json.dumps(["foo", [1, 2], {"optional1": "hello", "optional2": "dis working?"}]))

    time.sleep(1)  # give mqtt some time to make stuff happen
