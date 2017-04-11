from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet import task

# heartbeat every 10 mins, hard end for heartbeat 24 hrs
class CDSHeartBeat(object):
    def __init__(self, reactor=reactor, interval=0.1, hard_end_interval=2.0, hb_cb=None):
        self.reactor = reactor
        self.hb_callback = hb_cb
        self._hb_call = None

        self.hard_end_interval = hard_end_interval
        self.hard_end_timer = self.reactor.callLater(hard_end_interval, self._hard_end_timer)

        self.venue_heartbeat_interval = interval
        self._start_heartbeat_loop()

    def _start_heartbeat_loop(self):
        if self.hb_callback:
            self._hb_call = task.LoopingCall(self.hb_callback)
            self._hb_call.start(self.venue_heartbeat_interval, now=False)

    def stop_heartbeat_loop(self):
        if self._hb_call and self._hb_call.running:
            self._hb_call.stop()
            print("stop hb")
            self._hb_call = None

        if self.hard_end_timer is not None:
            if self.hard_end_timer.active():
                print("stop timer")
                self.hard_end_timer.cancel()
            self.hard_end_timer = None

    def _hard_end_timer(self):
        if self.hard_end_timer is not None:
            print("hard end timer")
            self.stop_heartbeat_loop()


class VenueHeartBeat(CDSHeartBeat):
    def __init__(self, venue_id, is_test, data):
        super(VenueHeartBeat, self).__init__()
        self.venue_id = venue_id
        self.is_test = is_test
        self.data = data
        self.data['event'] = 'venue-heartbeat'
        # self.hb_callback = classmethod(self._emit_venue_heartbeat)

    def _emit_venue_heartbeat(self):
        print("venue hb")


class ConfHeartBeat(CDSHeartBeat):
    def __init__(self, venue_id, is_test, data):
        super(ConfHeartBeat, self).__init__(hb_cb=self._emit_conf_heartbeat)
        self.venue_id = venue_id
        self.is_test = is_test
        self.data = data
        self.data['event'] = 'conf-heartbeat'
        # self.hb_callback = classmethod(self._emit_venue_heartbeat)

    def _emit_conf_heartbeat(self):
        print("conf hb")


conf_heartbeat = ConfHeartBeat('venue_id', 'is_test', {'data': 'test'})
venue_heartbeat = VenueHeartBeat('venue_id', 'is_test', {'data': 'test'})
# venue_heartbeat.stop_heartbeat_loop()
reactor.run()
# time.sleep(20)
print('done sleep')
