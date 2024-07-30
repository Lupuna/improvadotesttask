import typing
import sqlite3
import logging

class Connection(typing.ContextManager):
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')  # Используем временную базу данных для примера

    def execute(self, query: str, params: tuple):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


class DbManager:
    def open_connection(self) -> 'Connection':
        return Connection()


class WorkingHourManager:

    @staticmethod
    def log(employee_id, time) -> None:
        with DbManager().open_connection() as connection:
            logging.info(f'Logged working hours: {time}')
            connection.execute(
                'INSERT INTO working_log (employee_id, time_in_seconds) VALUES (?, ?)',
                (employee_id, time,)
            )

    @staticmethod
    def total(employee_id):
        with DbManager().open_connection() as connection:
            result = connection.execute(
                'SELECT SUM(time_in_seconds) FROM working_log WHERE employee_id = ?',
                (employee_id,)
            ).fetchone()
            total_time = result[0]/3600 if result[0] is not None else 0
            return total_time

    @staticmethod
    def salary(employee_id, date_from, date_to):
        with DbManager().open_connection() as connection:
            hour_rate = connection.execute(
                'SELECT hour_rate FROM employee_rates WHERE employee_id = ?',
                (employee_id,)
            ).fetchone()[0]

            total_time = connection.execute(
                'SELECT SUM(time_in_seconds) FROM working_log WHERE employee_id = ? AND time_in_seconds BETWEEN ? AND ?',
                (employee_id, date_from, date_to)
            ).fetchone()
            total_time = total_time[0]/3600 if total_time[0] is not None else 0

            return total_time * hour_rate
