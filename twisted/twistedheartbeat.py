from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet import task
import time

# heartbeat every 10 mins, hard end for heartbeat 24 hrs
class VenueHeartBeat(object):
    def __init__(self, venue_id, is_test, data, reactor=reactor, interval=0.1, hard_end_interval=2.0):
        self.reactor = reactor
        self.venue_id = venue_id
        self.is_test = is_test
        self.data = data
        self.data['event'] = 'venue-heartbeat'
        self.hard_end_interval = hard_end_interval
        self.hard_end_timer = None
        self.hard_end_timer = self.reactor.callLater(hard_end_interval, self._hard_end_timer)
        self.venue_heartbeat_interval = interval
        self._start_heartbeat_loop()
        print('init')


    def _start_heartbeat_loop(self):
        print('start hb')
        self._hb_call = task.LoopingCall(self._emit_venue_heartbeat)
        self._hb_call.start(0.1, now=False)

    def stop_heartbeat_loop(self):
        if self._hb_call and self._hb_call.running:
            print('stop hb')
            self._hb_call.stop()
            self._hb_call = None

        if self.hard_end_timer is not None:
            print('stop hard end timer')
            if self.hard_end_timer.active():
                self.hard_end_timer.cancel()
            self.hard_end_timer = None

    def _emit_venue_heartbeat(self):
        print('emit venue heartbeat')
#         cdm().emit_venue_data(self.venue_id, self.is_test, self.data)

    def _hard_end_timer(self):
        if self.hard_end_timer is not None:
            print('hard end timer')
            self.stop_heartbeat_loop()

venue_heartbeat = VenueHeartBeat('venue_id', 'is_test', {'data': 'test'})
# venue_heartbeat.stop_heartbeat_loop()
reactor.run()
# time.sleep(20)
print('done sleep')
