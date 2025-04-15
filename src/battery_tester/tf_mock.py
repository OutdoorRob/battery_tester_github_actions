# -*- coding: utf-8 -*-

# mock hardware functions
class TFConnectionMock:
    def __init__(self):
        self.voltage_current_v2 = TFBrickletVoltageCurrentV2Mock()

        self.ipcon = TFIPConnectionMock()

    @property
    def is_ready(self):
        return True


class TFIPConnectionMock:
    def disconnect(self):
        pass


class TFBrickletVoltageCurrentV2Mock:
    def __init__(self):
        self._values = ((0, 0), (0, 0), (21000, 4000), (20500, 3500), (20100, 3100),
                        (19800, 2800), (19600, 2600), (19500, 2500), (8500, 850),)
        self._index_voltage = 0
        self._index_current = 0

    def get_voltage(self):
        ret = self._values[self._index_voltage][0]
        self._index_voltage += 1

        if self._index_voltage == len(self._values):
            self._index_voltage = 0

        return ret

    def get_current(self):
        ret = self._values[self._index_current][1]
        self._index_current += 1

        if self._index_current == len(self._values):
            self._index_current = 0

        return ret
