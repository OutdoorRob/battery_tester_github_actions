# -*- coding: utf-8 -*-

import logging

import enum

import db_sqlite


# TODO Modularisieren damit auch Unit Tests möglich sind
# - Zugriff auf Datenbank und TF Hardware auslagern
# - Ergebnis ist ein fertiges 'TestRun'-Objekt mit allen Messwerten,
#   welches dann vom Hauptprogramm in ein

# TODO remove magic numbers (CONSTANTS or configureable by properties)

""" Ziel:
    - ein TestRun-Objekt
      - welches die Messwerte enthält
      - mit welchem ich auch nach Abschluss des Messlaufs noch Aktionen
        durchführen kann (z.B. Berechnung Kapazität)
    - Messen erfolgt zyklisch genau wie Aufruf der Funktion => Parameter
    - Schreiben TestRun + Messwerte reicht einmalig am Ende durch
      aufrufende Funktion zu.

"""

class TestRun:
    """ Was leibt übrig, wenn ich all die DB- und HW-Zugriffe raus nehme?
        Und handelt es sich dann noch um das Objekt / Modul, welches ich wollte?


    """

    TestState = enum.Enum('TestState', [('INITIAL', 0), ('WAITING', 1), ('RUNNING', 2), ('FINISHED', 3)])

    def __init__(self,
            database: db_sqlite.DBSQLite,
            battery_id: str,
            tool_version: str):

        self._db = database
        self._battery_id = battery_id
        self._tool_version = tool_version

        self._test_state = TestRun.TestState.INITIAL

        self._capacity_mAh = 0
        self._last_timestamp = None
        self._last_current_mA = None

        self._start_time = None
        self._end_time = None

        self._start_voltage_mV = None
        self._start_current_mA = None
        self._end_voltage_mV = None
        self._end_current_mA = None

    @property
    def capacity_mAh(self) -> float:
        return self._capacity_mAh

    @property
    def duration_s(self) -> float:
        if self._end_time and self._start_time:
            return (self._end_time - self._start_time).total_seconds()
        else:
            return 0.0

    @property
    def start_voltage_mV(self) -> int:
        return self._start_voltage_mV if self._start_voltage_mV else 0

    @property
    def start_current_mA(self) -> int:
        return self._start_current_mA if self._start_current_mA else 0

    @property
    def end_voltage_mV(self) -> int:
        return self._end_voltage_mV if self._end_voltage_mV else 0

    @property
    def end_current_mA(self) -> int:
        return self._end_current_mA if self._end_current_mA else 0


    """ Was tut die Funktion?
        - organisiert Aufbau des TestRun-Objektes (Metadaten + Messwerte)
        - definiert Start und Ende des Testablaufs anhand der aktuellen Messwerte
        - (fragt Messwerte bei HW an)
        - schreibt Messwerte in die Datenbank

        mögliche Erweiterungen für Flexibilität:
        - ein Schlüsselwert-Argument als Messwert welcher als Trigger für
          Start und Ende der Messung verwendet wird + beliebige viele weitere
          Messwerte als *args
        - nur timestamp, *args und args[0] ist als Trigger-Messwert vereinbart

        aktueller Nachteil:
        - Die test_run_id wird direkt am Anfang von Datenbank durch Aufruf von
          write_test_run() bezogen. Bei (theoretisch) mehreren parallen
          Testläufen würde es hier beim späteren Commit krachen. Es könnte nur
          der erste fertige Testlauf gespeichert werden.
          Noch schlimmer, die Messwerte aus mehreren Testläufen könnten einem
          einzigen Testlauf zugeordnet werden.
    """
    def call_test_cycle(self, timestamp, voltage_mV, current_mA) -> TestState:

        if self._test_state == TestRun.TestState.INITIAL:
            logging.debug("entry")
            self._test_run_id = self._db.write_test_run(
                self._battery_id,
                self._tool_version,
            )
            self._test_state = TestRun.TestState.WAITING

        if self._test_state == TestRun.TestState.WAITING:
            if voltage_mV > 10000:
                self._start_time = timestamp
                self._start_voltage_mV = voltage_mV
                self._start_current_mA = current_mA
                self._test_state = TestRun.TestState.RUNNING

        if self._test_state == TestRun.TestState.RUNNING:
            self._db.write_test_value(
                self._test_run_id,
                timestamp,
                voltage_mV,
                current_mA)

            if voltage_mV < 10000:
                self._test_state = TestRun.TestState.FINISHED
            else:
                self._end_time = timestamp
                self._end_voltage_mV = voltage_mV
                self._end_current_mA = current_mA

            self._calculate_capacity(timestamp, current_mA)

        if self._test_state == TestRun.TestState.FINISHED:
            #self._db.commit()
            logging.debug("exit")

        return self._test_state


    def _calculate_capacity(self, timestamp, current_mA):
        """Calculates capacity using the trapezoidal rule as numerical
        approximation.
        """

        if self._last_timestamp is not None:
            self._capacity_mAh += (
                (current_mA + self._last_current_mA) *
                (timestamp - self._last_timestamp).total_seconds() / 2 / 3600)

        self._last_timestamp = timestamp
        self._last_current_mA = current_mA


class TestValues:
    pass