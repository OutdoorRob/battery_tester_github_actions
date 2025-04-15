# -*- coding: utf-8 -*-

import tkinter as tk


WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

class TkinterGUI:
    """
    Represents the main application containing the top level widget (root
    window).
    """

    CMD_BUTTON_START_TEST_RUN = 1

    def __init__(self, version: str):

        self._button_commands = {}

        # root window
        self._root_window = tk.Tk()
        self._root_window.title(f"Battery Tester {version}")
        self._root_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self._main_frame = TkinterMainFrame(self)
        self._status_bar = TkinterStatusBar(self)

    @property
    def battery_id(self) -> str:
        return self._main_frame._ent_battery_id.get()

    def set_test_state(self, ready: bool, text: str) -> None:
        self._main_frame._lbl_test_state["text"] = text
        if ready:
            self._main_frame._btn_start_test_run.config(state="normal")
            self._main_frame._ent_battery_id.config(state="normal")
        else:
            self._main_frame._btn_start_test_run.config(state="disabled")
            self._main_frame._ent_battery_id.config(state="disabled")

    def set_actual_voltage(self, voltage_mV: int) -> None:
        self._main_frame._lbl_actual_voltage["text"] = f"{(voltage_mV / 1000):.2f} V"

    def set_actual_current(self, current_mA: int) -> None:
        self._main_frame._lbl_actual_current["text"] = f"{(current_mA / 1000):.2f} A"

    def set_actual_capacity(self, capacity_mAh: int) -> None:
        self._main_frame._lbl_actual_capacity["text"] = f"{capacity_mAh:.0f} mAh"

    def set_actual_duration(self, duration_s: int) -> None:
        self._main_frame._lbl_actual_duration["text"] = f"{duration_s:.0f} s"

    def set_statistics_start_voltage(self, voltage_mV: int) -> None:
        self._main_frame._lbl_statistics_start_voltage["text"] = \
            self._main_frame._lbl_statistics_start_voltage ._text_format.format(voltage_mV / 1000)

    def set_statistics_start_current(self, current_mA: int) -> None:
        self._main_frame._lbl_statistics_start_current["text"] = \
            self._main_frame._lbl_statistics_start_current ._text_format.format(current_mA / 1000)

    def set_statistics_end_voltage(self, voltage_mV: int) -> None:
        self._main_frame._lbl_statistics_end_voltage["text"] = \
            self._main_frame._lbl_statistics_end_voltage ._text_format.format(voltage_mV / 1000)

    def set_statistics_end_current(self, current_mA: int) -> None:
        self._main_frame._lbl_statistics_end_current["text"] = \
            self._main_frame._lbl_statistics_end_current ._text_format.format(current_mA / 1000)

    def set_status_database(self, connected: bool):
        if connected:
            self._status_bar._lbl_status_database.config(background="lime green")
        else:
            self._status_bar._lbl_status_database.config(background="red")

    def set_status_tinkerforge(self, connected: bool):
        if connected:
            self._status_bar._lbl_status_tinkerforge.config(background="lime green")
        else:
            self._status_bar._lbl_status_tinkerforge.config(background="red")

    def register_callback(self, cmd_id, function):
        self._button_commands[cmd_id] = function

        match cmd_id:
            case TkinterGUI.CMD_BUTTON_START_TEST_RUN:
                self._main_frame._btn_start_test_run["command"] = function

    def after(self, ms : int, func, *args):
        return self._root_window.after(ms, func, *args)

    def mainloop(self):
        self._root_window.mainloop()


class TkinterMainFrame(tk.Frame):
    """Represents the main frame with its widgets."""
    def __init__(self, app: TkinterGUI):
        super().__init__(app._root_window, cursor="hand2")

        self.pack(fill="both", expand=True)

        self._create_widgets_test_run()
        self._create_widgets_actual_measurements()
        self._create_widgets_statistics()

    def _create_widgets_test_run(self):
        # group
        self._grp_test_run = tk.LabelFrame(self)
        self._grp_test_run.pack(side="top", ipadx=2, ipady=2)

        # label for test run status information
        self._lbl_test_state = tk.Label(
            self._grp_test_run,
            text="Programm wird initialisiert...",
        )
        self._lbl_test_state.pack()

        # single line text field to enter battery id
        # TODO replace by combo box
        self._ent_battery_id = tk.Entry(self._grp_test_run)
        self._ent_battery_id.pack()

        # button 'Start Test'
        self._btn_start_test_run = tk.Button(
            self._grp_test_run,
            text="Start Test",
            state="disabled",
        )
        self._btn_start_test_run.pack()

    def _create_widgets_actual_measurements(self):
        # group
        self._grp_actual_measurements = tk.LabelFrame(self)
        self._grp_actual_measurements.pack(side="top", ipadx=2, ipady=2)

        # labels for actual measurements
        self._lbl_actual_voltage = tk.Label(
            self._grp_actual_measurements,
            text="0.00 V",
        )
        self._lbl_actual_voltage.pack()

        self._lbl_actual_current = tk.Label(
            self._grp_actual_measurements,
            text="0.00 A",
        )
        self._lbl_actual_current.pack()

        self._lbl_actual_capacity = tk.Label(
            self._grp_actual_measurements,
            text="0 mAh",
        )
        self._lbl_actual_capacity.pack()

        self._lbl_actual_duration = tk.Label(
            self._grp_actual_measurements,
            text="0 s",
        )
        self._lbl_actual_duration.pack()

    def _create_widgets_statistics(self):
        # group
        self._grp_statistics = tk.LabelFrame(self)
        self._grp_statistics.pack(side="top", ipadx=2, ipady=2)

        # labels for statistics
        self._lbl_statistics_start_voltage = tk.Label(
            self._grp_statistics,
            anchor="e",
        )
        self._lbl_statistics_start_voltage._text_format = \
            "Spannung nach dem Einschalten: {:.2f} V"
        self._lbl_statistics_start_voltage["text"] = \
            self._lbl_statistics_start_voltage._text_format.format(0)
        self._lbl_statistics_start_voltage.pack(fill="x")

        self._lbl_statistics_start_current = tk.Label(
            self._grp_statistics,
            anchor="e",
        )
        self._lbl_statistics_start_current._text_format = \
            "Strom nach dem Einschalten: {:.2f} A"
        self._lbl_statistics_start_current["text"] = \
            self._lbl_statistics_start_current._text_format.format(0)
        self._lbl_statistics_start_current.pack(fill="x")

        self._lbl_statistics_end_voltage = tk.Label(
            self._grp_statistics,
            anchor="e",
        )
        self._lbl_statistics_end_voltage._text_format = \
            "Spannung vor dem Abschalten: {:.2f} V"
        self._lbl_statistics_end_voltage["text"] = \
            self._lbl_statistics_end_voltage._text_format.format(0)
        self._lbl_statistics_end_voltage.pack(fill="x")

        self._lbl_statistics_end_current = tk.Label(
            self._grp_statistics,
            anchor="e",
        )
        self._lbl_statistics_end_current._text_format = \
            "Strom vor dem Abschalten: {:.2f} A"
        self._lbl_statistics_end_current["text"] = \
            self._lbl_statistics_end_current._text_format.format(0)
        self._lbl_statistics_end_current.pack(fill="x")


class TkinterStatusBar(tk.Frame):
    """Represents the status bar (as a separate frame)."""
    def __init__(self, app: TkinterGUI):
        super().__init__(app._root_window, cursor="hand1")

        self.pack(side="bottom", fill="x")

        self._create_widgets()

    def _create_widgets(self):
        # database
        self._lbl_status_database = tk.Label(
            self,
            text="Database",
            anchor="center",
            background="red",
            relief="sunken",
            bd=1,
        )
        self._lbl_status_database.pack(side="right", ipadx=3, ipady=2)

        # TinkerForge
        self._lbl_status_tinkerforge = tk.Label(
            self,
            text="TinkerForge",
            anchor="center",
            background="red",
            relief="sunken",
            bd=1,
        )
        self._lbl_status_tinkerforge.pack(side="right", ipadx=3, ipady=2)

        # spacer (to fill up empty space)
        self._lbl_status_spacer = tk.Label(
            self,
            text="",
            anchor="center",
            relief="sunken",
            bd=1,
        )
        self._lbl_status_spacer.pack(fill="x")
