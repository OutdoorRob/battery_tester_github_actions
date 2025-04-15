# -*- coding: utf-8 -*-

import sqlite3

class DBSQLite:
    def __init__(self, database_path: str):
        self._database_path = database_path
        self._connection = None
        self._cursor = None

        # TODO SQL Verbindung über mehrere Threads: Ist Connection oder Cursor das Problem?
        # TODO DB Klasse umbauen: maximal connection global aber nicht den Cursor
        self._connection = sqlite3.connect(self._database_path)
        self._connection.execute("PRAGMA foreign_keys = 1")

        self._cursor = self._connection.cursor()

        self._init_database_if_empty()

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()

    def write_test_run(
            self,
            battery_id: str,
            tool_version: str = "",
            hw_versions: str = "",
            notes: str = "",
        ) -> int | None:

        try:
            return self._cursor.execute("""
                INSERT INTO "test_run" (
                    "fk_battery_id",
                    "tool_version",
                    "hw_versions",
                    "notes"
                )
                VALUES (?, ?, ?, ?);""",
                (battery_id, tool_version, hw_versions, notes)
            ).lastrowid
        except:
            self._connection.rollback()
            raise

    def write_test_value(
            self,
            test_run_id: int,
            timestamp,
            voltage_mV: int,
            current_mA: int,
        ) -> None:
        try:
            self._cursor.execute("""
                INSERT INTO "test_value" (
                    "fk_test_run_id",
                    "datetime",
                    "voltage_mV",
                    "current_mA"
                )
                VALUES (?, ?, ?, ?);""",
                (test_run_id, timestamp, voltage_mV, current_mA)
            )
        except:
            self._connection.rollback()
            raise

    # TODO Datenbankschema / SQL-Querys in separate Datei auslagern
    def _init_database_if_empty(self):

        try:
            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS "battery" (
                    "id" TEXT NOT NULL UNIQUE,
                    "battery_code" TEXT NOT NULL,
                    "battery_serial_number" TEXT NOT NULL,
                    "device_code" TEXT NOT NULL,
                    "device_serial_number" TEXT,
                    "capacity_mAh" INTEGER NOT NULL,
                    "cell_type" TEXT NOT NULL,
                    "cell_count" INTEGER NOT NULL,
                    "cell_capacity_mAh" INTEGER,
                    "pcb_version" TEXT,
                    "eeprom_version" TEXT,
                    CONSTRAINT "battery_pk"
                        PRIMARY KEY("id")
                );"""
            )

            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS "battery_history" (
                    "id" INTEGER NOT NULL UNIQUE,
                    "fk_battery_id" INTEGER NOT NULL,
                    "notes" TEXT,
                    CONSTRAINT "battery_history_pk"
                        PRIMARY KEY("id" AUTOINCREMENT),
                    CONSTRAINT "battery_history_fk_battery_id"
                        FOREIGN KEY("fk_battery_id")
                            REFERENCES "battery"("id")
                );"""
            )

            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS "test_run" (
                    "id" INTEGER NOT NULL UNIQUE,
                    "fk_battery_id" TEXT NOT NULL,
                    "tool_version" TEXT,
                    "hw_versions" TEXT,
                    "notes" TEXT,
                    CONSTRAINT "test_run_pk"
                        PRIMARY KEY("id" AUTOINCREMENT),
                    CONSTRAINT "test_run_fk_battery_id"
                        FOREIGN KEY("fk_battery_id")
                            REFERENCES "battery"("id")
                );"""
            )

            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS 'test_value' (
                    "id" INTEGER NOT NULL UNIQUE,
                    "fk_test_run_id" INTEGER NOT NULL,
                    "datetime" TEXT NOT NULL,
                    "voltage_mV" INTEGER NOT NULL,
                    "current_mA" INTEGER NOT NULL,
                    CONSTRAINT "test_value_pk"
                        PRIMARY KEY("id" AUTOINCREMENT),
                    CONSTRAINT "test_value_fk_test_run_id"
                        FOREIGN KEY("fk_test_run_id")
                            REFERENCES "test_run"("id")
                );"""
            )


            # test code
            # self._batteries = (("SV10-Nr005", "215681", "", "SV10", "", 2800, "", 6, 0, "", ""),
            #                    ("SV10-Nr004", "238168", "", "SV10", "", 2400, "", 6, 0, "", ""),
            #                    ("SV25-Nr003", "215681", "", "SV25", "", 2800, "", 6, 0, "", ""),
            #                    ("test", "123456", "", "SV-Test", "", 9999, "", 6, 0, "", ""),)

            # self._cursor.executemany("""
            #     INSERT INTO "battery" (
            #         "id",
            #         "battery_code",
            #         "battery_serial_number",
            #         "device_code",
            #         "device_serial_number",
            #         "capacity_mAh",
            #         "cell_type",
            #         "cell_count",
            #         "cell_capacity_mAh",
            #         "pcb_version",
            #         "eeprom_version"
            #     )
            #     VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            #     self._batteries
            # )

            self._connection.commit()
        except:
             self._connection.rollback()
             raise


    # @property
    # def database_path(self):
    #     return self._database_path