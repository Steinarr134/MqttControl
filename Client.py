import json
import inspect


class Communicatable(object):
    """
    This subclass handles get, set and call communication through mqtt

        set requests should arrive as a json wrapped dictionary with key-value
        pairs of things to set
        example:
                    json.dumps({"gain": 2.4, "exposuretime": 400})

        get requests should arrive as a json wrapped list of keys to get,
        they will then be published on main
        example:
                    json.dumps(["gain", "exposuretime"])

        call requests should arrive as a json three piece tuple on the form:
                                ( <function name>, <list of args>, <dict of kwargs>)
        example:
                    json.dumps(("my_method", [arg1, arg2], {"kwarg1": 1, "kwarg2": 2}))



    see 'if __main__' below for example on how to inherit this class

    """
    def __init__(self, mqtt, who):
        self._mqtt = mqtt
        self._mqtt_who = who

        # subscribe to get, set and call
        self._mqtt_subscribe(who + "/set", self._mqtt_set)
        self._mqtt_subscribe(who + "/get", self._mqtt_get)
        self._mqtt_subscribe(who + "/call", self._mqtt_call)

        # keep track of which class variables are settable, gettable and callable to prevent spurious controlling
        self._mqtt_settable = []
        self._mqtt_gettable = []
        self._mqtt_callable = {}

    def _mqtt_subscribe(self, topic, callback):
        self._mqtt.subscribe(topic)
        self._mqtt.message_callback_add(topic, callback)

    def mqtt_settable(self, key):
        self.mqtt_readable(key)
        self._mqtt_settable.append(key)

    def mqtt_readable(self, key):
        # make sure key is an attribute no need to handle the exception
        #  as these functions should only be called during startup and configuration of classes.
        assert key in dir(self)

        self._mqtt_gettable.append(key)

    def mqtt_callable(self, key, func=None):
        if func is None:
            func = self.__getattribute__(key)
        # make sure func is a callable attribute
        assert "__call__" in dir(func)
        # use ascii version of string since that is what mqtt uses
        self._mqtt_callable[key] = func

    def _mqtt_call(self, _, __, msg):
        print("got call", msg.payload)
        funcname, args, kwargs = json.loads(msg.payload)
        print(f"{type(funcname)=}")
        print(funcname, self._mqtt_callable)
        if funcname in self._mqtt_callable:
            try:
                self._mqtt_callable[funcname](*args, **kwargs)
            except (TypeError, ValueError) as e:
                print(f"{e} in Communicatable._mqtt_call when calling "
                      f"{funcname}(*{args}, **{kwargs}). The signature of {funcname} is:"
                      f"{funcname}{str(inspect.signature(self._mqtt_callable[funcname]))}")

    def _mqtt_set(self, _, __, msg):
        msg = json.loads(msg.payload)
        # print("mqtt_set", msg)
        pub = {}
        for key, val in msg.items():
            if key in self._mqtt_settable:
                # print("setting ", key, "to ", val)
                self.__setattr__(key, val)
                pub[key] = self.__getattribute__(key)

        if pub:
            self._mqtt.publish(self._mqtt_who, json.dumps(pub))

    def _mqtt_get(self, _, __, msg):
        msg = json.loads(msg.payload)
        pub = {}
        for key in msg:
            if key in self._mqtt_gettable:
                pub[key] = self.__getattribute__(key)
        if pub:
            self._mqtt.publish(self._mqtt_who, json.dumps(pub))

    def mqtt_publish(self, stuff):
        self._mqtt.publish(self._mqtt_who, stuff)
