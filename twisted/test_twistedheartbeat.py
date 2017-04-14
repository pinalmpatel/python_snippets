#! /usr/bin/python

from twisted.trial.unittest import TestCase
from twisted.internet import defer, reactor, task

import call_diagnostic_manager as cdm
import http_helper
import mock
import settings
import simplejson

class CDSHeartBeatTest(TestCase):
    def setUp(self):

        self.reactor_mock = mock.MagicMock()
        self.hb_callback = mock.MagicMock()

        with mock.patch.object(settings, 'call_diagnostic_heartbeat_interval') as settings_mock1:
            with mock.patch.object(settings, 'call_diagnostic_heartbeat_hard_end_interval') as settings_mock2:
                with mock.patch.object(task, 'LoopingCall') as mock_loopingcall:
                    settings_mock1.return_value = 5*60.0
                    settings_mock2.return_value = 15*60*60.0
                    self.mock_loopingcall = mock_loopingcall
                    self.hb_call = self.mock_loopingcall.return_value

                    self.cdshb = cdm.CDSHeartBeat(reactor=self.reactor_mock, hb_callback=self.hb_callback)
                    self.timer = self.reactor_mock.callLater.return_value

    def tearDown(self):
        if self.cdshb is not None:
            self.cdshb.stop_heartbeat_loop()

    def test_init(self):
        self.assertEquals(self.reactor_mock.callLater.call_count, 1)
        self.assertEquals(self.reactor_mock.callLater.call_args[0][0], self.cdshb.hard_end_interval)

        self.assertEquals(self.mock_loopingcall.call_count, 1)
        self.assertEquals(self.mock_loopingcall.call_args[0][0], self.hb_callback)
        self.assertEquals(self.hb_call.start.call_count, 1)
        self.assertEquals(self.hb_call.start.call_args[0][0], self.cdshb.heartbeat_interval)

    def test_stop_heartbeat_loop(self):
            self.cdshb.stop_heartbeat_loop()
            self.assertEquals(self.hb_call.stop.call_count, 1)
            self.assertEquals(self.timer.active.call_count, 1)
            self.assertEquals(self.timer.cancel.call_count, 1)

    def test_hard_end_timer(self):
        with mock.patch.object(cdm.CDSHeartBeat, 'stop_heartbeat_loop') as stop_hb_mock:
            self.cdshb._hard_end_timer()
            self.assertEquals(stop_hb_mock.call_count, 1)


class VenueHeartBeatTest(TestCase):
    def setUp(self):
        self.venue_id = 'venue_id'
        self.is_test = 'is_test'
        self.data = {'fqdn': 'fqdn', 'conferenceID': 'test'}

        self.reactor_mock = mock.MagicMock()

        with mock.patch.object(settings, 'call_diagnostic_url') as settings_mock1:
            with mock.patch.object(settings, 'call_diagnostic_emit_delay_secs') as settings_mock2:
                with mock.patch.object(settings, 'call_diagnostic_emit_max_count') as settings_mock3:
                    settings_mock1.return_value = 'remote url'
                    settings_mock2.return_value = 1.0
                    settings_mock3.return_value = 10
                    self.cdm = cdm.CallDiagnosticManager(reactor=self.reactor_mock)

        with mock.patch.object(settings, 'call_diagnostic_heartbeat_interval') as settings_mock1:
            with mock.patch.object(settings, 'call_diagnostic_heartbeat_hard_end_interval') as settings_mock2:
                with mock.patch.object(task, 'LoopingCall') as mock_loopingcall:
                    with mock.patch.object(cdm.VenueHeartBeat, '_emit_venue_heartbeat') as emit_hb_mock:
                        settings_mock1.return_value = 5*60.0
                        settings_mock2.return_value = 15*60*60.0
                        self.mock_loopingcall = mock_loopingcall
                        self.emit_hb_mock = emit_hb_mock
                        self.hb_callback = self.mock_loopingcall.return_value

                        self.vhb = cdm.VenueHeartBeat(self.venue_id, self.is_test, self.data, reactor=self.reactor_mock)
                        self.timer = self.reactor_mock.callLater.return_value

    def tearDown(self):
        if self.vhb is not None:
            self.vhb.stop_heartbeat_loop()

    def _validate_pending_venue_activity(self, activity, msg_type, msg_data):
        self.assertEquals(activity.venue_id, self.venue_id)
        self.assertEquals(activity.msg_type, msg_type)
        msg_data['event'] = 'venue-heartbeat'
        self.assertEquals(activity.msg_data, msg_data)
        self.assertEquals(activity.is_test, self.is_test)

    def test_init(self):
        self.assertEquals(self.mock_loopingcall.call_count, 1)
        self.assertEquals(self.mock_loopingcall.call_args[0][0], self.emit_hb_mock)

    def test_emit_venue_heartbeat(self):
        with mock.patch('call_diagnostic_manager.cdm') as global_cdm_mock:
            global_cdm_mock.return_value = self.cdm
            self.vhb._emit_venue_heartbeat()
            self.assertEquals(len(self.cdm.pending_diagnotics), 1)
            self._validate_pending_venue_activity(self.cdm.pending_diagnotics[0], cdm.diagnostic_msg_type_venue_data, self.data)
