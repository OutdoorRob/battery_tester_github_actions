#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" docstring main
    ...
"""

from datetime import datetime

import db_sqlite
import tf_connection
import tf_mock
from gui.tkinter_app import TkinterGUI
from testrun import TestRun

import logging


__version__ = "0.0.2"

""" # TODO
    - DB Klasse umbauen
        - maximal connection global aber nicht den Cursor
        - prüfen ob dann 'check_same_thread=False' noch nötig ist
    - Live Anzeige Entladekurve
    - Export der Messwerte als CSV (+ automatisch nach jedem fertigen Messdurchlauf)
    - Berechnung der Kapazität + Anzeige -> done
        - eigener Algorithmus -> done
        - mit Numpy Integral
    - Log-Boschaften überarbeiten (Prozess-Nr. nach vorn, variable Nachricht als letztes)
"""

""" Learnings
    - working with modules threading, sqlite3, tkinter
    - designing a database
    - controlling external hardware with a Python programm
    - working with callbacks and multithreaded programms
    - reading and understanding other peoples code
    - maintaining a project
"""

""" Erkenntnis
    Meine Modularisierung ist nicht wirklich modular.

    Ich habe ein Projekt, weiß was es machen soll und unterteile es in grobe
    Bestandteile (z.B. main, GUI, DB, Hardware...).
    Ziel des Ganzen ist es, die main-Datei bzw. main-Funktion sehr schlank
    zu halten, so dass diese nur wie ein 'Inhaltsverzeichnis' von
    BlackBox-Funktionen wirkt, welche nacheinander aufgerufen werden.

    ABER: Dabei wandern viele Abhängigkeiten und Kreuzverweise in die anderen
    'Module'. Es sind keine wirklichen Module sondern nur Auslagerungen von
    Funktionalitäten des Hauptproramms in andere Dateien!

    Das führt zu:
    - einer noch komplexeren Struktur als ein einzige lange main-Datei
    - gaukelt eine Modularisierung vor die es nicht gibt
    - beim Schreiben von Unit Tests fragt man sich, wie man ein so komplexes
      'Modul' testen soll (z.B. testrun, welche auf DB und HW zugreift)

    Am Ende muss der Code irgendwo stehen.
    Die Frage ist, wie kann man diesen wirklich modular auf Klassen und
    Dateien verteilen?
    Wie flexibel und wiederverwendbar können / müssen diese Module dann sein?
    Ich schreibe hier keine Templates, Datentypen oder low-level Funktionen.
    Es handelt sich (aktuell) um ein ganz spezielles Programm, welches
    spezielle HW verwendet und in eine spezifisch definierte Datenbank schreibt.

"""

""" notes
    - tinkerforge.ip_connection.IPConnection starts three threads:
        - 'Callback-Processor'
        - 'Disconnect-Prober'
        - 'Brickd-Receiver'
    - tkinter and threads:
        - https://www.reddit.com/r/learnpython/comments/10qzto6/how_does_tkinter_multithreading_work_and_why/
        - https://tkdocs.com/tutorial/eventloop.html

"""

# - - - helper functions / debug outputs  - - - - - - - - - - - - - - - - - - -
logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    #format="{asctime} - {funcName}(): '{message}' ({process}, {thread})",
    format="{asctime:<10} {funcName:<20} {message:<30} ({process}, {thread})",
    datefmt="%H:%M:%S")


# - - - main module - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# TODO in Klasse Main auslagern
gui : TkinterGUI
database : db_sqlite.DBSQLite
tinkerforge : tf_connection.TFIPConnection | tf_mock.TFConnectionMock


def check_tinkerforge_connection():
    if tinkerforge.is_ready:
        gui.set_status_tinkerforge(True)
        gui.set_test_state(True, "Bereit für Messung.")
    else:
        gui.after(100, check_tinkerforge_connection)

def cmd_start_test_run_cyclic():

    gui.set_test_state(False, "Messung läuft...")

    schedule_test_run(
        1000,
        TestRun(
            database,
            gui.battery_id,
            __version__,
        )
    )

def schedule_test_run(time_ms: int, test_run: TestRun):

    _voltage_mV = tinkerforge.voltage_current_v2.get_voltage()
    _current_mA = tinkerforge.voltage_current_v2.get_current()

    try:
        _state = test_run.call_test_cycle(datetime.now(), _voltage_mV, _current_mA)
    except db_sqlite.sqlite3.IntegrityError:
        gui.set_test_state(True, "Messung fehlgeschlagen! Bereit für neue Messung.")
    else:
        gui.set_actual_voltage(_voltage_mV)
        gui.set_actual_current(_current_mA)
        gui.set_actual_capacity(test_run.capacity_mAh)
        gui.set_actual_duration(test_run.duration_s)

        if _state == TestRun.TestState.FINISHED:
            gui.set_test_state(True, "Messung erfolgreich! Bereit für neue Messung.")

            gui.set_statistics_start_voltage(test_run.start_voltage_mV)
            gui.set_statistics_start_current(test_run.start_current_mA)
            gui.set_statistics_end_voltage(test_run.end_voltage_mV)
            gui.set_statistics_end_current(test_run.end_current_mA)
        else:
            gui.after(time_ms, schedule_test_run, time_ms, test_run)


def main():
    global gui, database, tinkerforge

    gui = TkinterGUI(__version__)

    database = db_sqlite.DBSQLite("out/battery_tester.db")
    #tinkerforge = tf_connection.TFIPConnection()
    tinkerforge = tf_mock.TFConnectionMock()

    gui.register_callback(
        TkinterGUI.CMD_BUTTON_START_TEST_RUN,
        cmd_start_test_run_cyclic,
    )

    # setup GUI
    gui.set_status_database(database)

    # start schedulers
    check_tinkerforge_connection()

    # transfer control to tk mainloop()
    gui.mainloop()

    tinkerforge.ipcon.disconnect()
    database.close()


if __name__ == "__main__":
    logging.debug("entry")

    main()

    logging.debug("exit")
