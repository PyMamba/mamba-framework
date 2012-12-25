# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Asynchronous JSON response
"""

from json import JSONEncoder

from twisted.internet.task import cooperate


class AsyncJSON(object):
    """
    Asynchronous JSON response.

    I use a cooperate Twisted task in order to create a producer that
    send huge amounts of JSON data in an asynchronous way.

    If the data being serialized into JSON is huge, the serialization
    process can take longest than the browser waiting response and can
    block itself the web server, preventing other requests from being
    serviced. This class prevents that type of inconveniences.

    This class is based on Jean Paul Calderone post at:
        http://jcalderone.livejournal.com/55680.html
    """

    def __init__(self, value):
        self._value = value

    def begin(self, consumer):
        self._consumer = consumer
        self._iterable = JSONEncoder().iterencode(self._value)
        self._consumer.registerProducer(self, True)
        self._task = cooperate(self._produce())
        defer = self._task.whenDone()
        defer.addBoth(self._unregister)
        return defer

    def pause(self):
        self._task.pause()

    def resume(self):
        self._task.resume()

    def stop(self):
        self._task.stop()

    def _produce(self):
        for chunk in self._iterable:
            self._consumer.write(chunk)
            yield None

    def _unregister(self, passthrough):
        self._consumer.unregisterProducer()
        return passthrough

    def pauseProducing(self):
        self.pause()

    def resumeProducing(self):
        self.resume()

    def stopProducing(self):
        self.stop()
