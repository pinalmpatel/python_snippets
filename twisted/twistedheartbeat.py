#! /usr/bin/python
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet import task
import time

# heartbeat every interval seconds, hard end for heartbeat hard_end_interval seconds
class CDSHeartBeat(object):
    def __init__(self, reactor=reactor, hb_callback=None):
        self.reactor = reactor
        self.hb_callback = hb_callback
        self._hb_call = None

        # self.hard_end_interval = settings.call_diagnostic_heartbeat_hard_end_interval()
        self.hard_end_interval = 3
        self.hard_end_timer = self.reactor.callLater(self.hard_end_interval, self._hard_end_timer)

        # self.heartbeat_interval = settings.call_diagnostic_heartbeat_interval()
        self.heartbeat_interval = 0.1
        self._start_heartbeat_loop()

    def __del__(self):
        self.stop_heartbeat_loop()

    def _start_heartbeat_loop(self):
        if self.hb_callback:
            self._hb_call = task.LoopingCall(self.hb_callback)
            self._hb_call.start(self.heartbeat_interval, now=False)

    def stop_heartbeat_loop(self):
        if self._hb_call and self._hb_call.running:
            self._hb_call.stop()
            self._hb_call = None

        if self.hard_end_timer is not None:
            if self.hard_end_timer.active():
                self.hard_end_timer.cancel()
            self.hard_end_timer = None

    def _hard_end_timer(self):
        if self.hard_end_timer is not None:
            self.stop_heartbeat_loop()


class VenueHeartBeat(CDSHeartBeat):
    def __init__(self, venue_id, is_test, data, reactor=reactor):
        super(VenueHeartBeat, self).__init__(hb_callback=self._emit_venue_heartbeat, reactor=reactor)
        self.venue_id = venue_id
        self.is_test = is_test
        self.data = data
        self.data['event'] = 'venue-heartbeat'

    def _emit_venue_heartbeat(self):
        print 'venue hb'
        # cdm().emit_venue_data(self.venue_id, self.is_test, self.data)


class ConfHeartBeat(CDSHeartBeat):
    def __init__(self, venue_id, is_test, data, reactor=reactor):
        super(ConfHeartBeat, self).__init__(reactor=reactor, hb_cb=self._emit_conf_heartbeat)
        self.venue_id = venue_id
        self.is_test = is_test
        self.data = data
        self.data['event'] = 'conf-heartbeat'

    def _emit_conf_heartbeat(self):
        print("conf hb")

@defer.inlineCallbacks
def _main():
    # conf_heartbeat = ConfHeartBeat('venue_id', 'is_test', {'data': 'test'})
    venue_heartbeat = {}
    venue_heartbeat[1] = VenueHeartBeat('venue_id', 'is_test', {'data': 'test'})
    time.sleep(2)
    # venue_heartbeat.pop('1', None)
    # venue_heartbeat.stop_heartbeat_loop()
    # time.sleep(20)
    print('done sleep')

reactor.callWhenRunning(_main)
reactor.run()

