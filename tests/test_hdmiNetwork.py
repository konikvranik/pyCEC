from unittest import TestCase

from pycec import HdmiNetwork, HdmiDevice


class TestHdmiNetwork(TestCase):
    pass

    def test_scan(self):
        network = HdmiNetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False, False, False, False, False, False,
             False]))
        network.scan()
        self.assertIn(HdmiDevice(0), network.devices)

    def test_devices(self):
        network = HdmiNetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False, False, False, False, False, False,
             False]))
        network.scan()
        for i in [0, 1, 3, 5]:
            self.assertIn(HdmiDevice(i), network.devices)
        for i in [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            self.assertNotIn(HdmiDevice(i), network.devices)


class MockAdapter(object):
    def __init__(self, data):
        self._data = data

    def PollDevice(self, i):
        return self._data[i]
