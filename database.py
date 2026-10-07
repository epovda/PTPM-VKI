import sqlite3


class Database:

    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                login            TEXT NOT NULL,
                password         TEXT NOT NULL,
                confirm_password TEXT NOT NULL,
                result           INTEGER NOT NULL,
                error_message    TEXT,
                PRIMARY KEY (login, password, confirm_password)
            )
            """
        )
        self._conn.commit()

    def add_record(self, login, password, confirm_password, result, error_message):
        self._conn.execute(
            "INSERT OR REPLACE INTO records VALUES (?, ?, ?, ?, ?)",
            (login, password, confirm_password, int(result), error_message),
        )
        self._conn.commit()

    def get_record(self, login, password, confirm_password):
        cur = self._conn.execute(
            "SELECT result, error_message FROM records "
            "WHERE login=? AND password=? AND confirm_password=?",
            (login, password, confirm_password),
        )
        return cur.fetchone()

    def delete_record(self, login, password, confirm_password):
        self._conn.execute(
            "DELETE FROM records WHERE login=? AND password=? AND confirm_password=?",
            (login, password, confirm_password),
        )
        self._conn.commit()

    def close(self):
        self._conn.close()