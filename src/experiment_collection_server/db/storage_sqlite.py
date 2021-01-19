import datetime
import sqlite3
import typing

from .storage_abc import StorageABC

INIT_STATEMENT = """CREATE TABLE IF NOT EXISTS experiments
(
    namespace  text,
    name       text,
    params     text,
    metrics    text,
    created_at timestamp not null,
    expires_at timestamp,
    PRIMARY KEY (namespace, name)
);
CREATE TABLE IF NOT EXISTS tokens
(
    id         integer PRIMARY KEY AUTOINCREMENT,
    token      text not null UNIQUE,
    created_at timestamp not null DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp
);
CREATE TABLE IF NOT EXISTS token_collection
(
    token     integer not null,
    namespace text    not null,
    FOREIGN KEY (token) REFERENCES tokens (id),
    FOREIGN KEY (namespace) REFERENCES experiments (namespace),
    PRIMARY KEY (token, namespace)
);"""


class StorageSQLite(StorageABC):

    def __init__(self, path='main.db'):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        with self.conn:
            self.conn.executescript(INIT_STATEMENT)

    def close(self):
        self.conn.close()

    def check_permission(self, token: str, namespace: str) -> bool:
        sql = """SELECT 1
FROM token_collection
         INNER JOIN tokens ON token_collection.token = tokens.id
WHERE tokens.expires_at IS NULL
  AND tokens.token = ?
  AND token_collection.namespace = ?;"""
        return self.conn.execute(sql, (token, namespace,)).fetchone() is not None

    def _delete_outdated(self):
        sql = """DELETE
FROM experiments
WHERE expires_at < datetime('now'); """
        with self.conn:
            self.conn.execute(sql)

    def reserve_experiment(self, namespace: str, name: str, duration: int) -> bool:
        if self.check_experiment(namespace, name):
            return False
        self._delete_outdated()
        sql = """INSERT INTO experiments (namespace, name, created_at, expires_at)
VALUES (?, ?, datetime('now'), datetime('now', ?));"""
        try:
            with self.conn:
                self.conn.execute(sql, (namespace, name, '+{} seconds'.format(duration)))
            return True
        except sqlite3.IntegrityError:
            return False

    # pylint: disable=R0913
    def create_experiment(self, namespace: str, name: str, params: str, metrics: str, time: datetime.datetime) -> bool:
        sql1 = """DELETE
FROM experiments
WHERE expires_at IS NOT NULL
  AND namespace = ?
  AND name = ?"""
        sql2 = """INSERT INTO experiments (namespace, name, params, metrics, created_at)
VALUES (?, ?, ?, ?, ?);"""
        self._delete_outdated()
        try:
            with self.conn:
                self.conn.execute(sql1, (namespace, name,))
                self.conn.execute(sql2, (namespace, name, params, metrics, time,))
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_experiment(self, namespace: str, name: str):
        sql = """DELETE
FROM experiments
WHERE namespace = ?
  AND name = ?;"""
        self._delete_outdated()
        with self.conn:
            self.conn.execute(sql, (namespace, name,))

    def check_experiment(self, namespace: str, name: str) -> bool:
        sql = """SELECT 1
FROM experiments
WHERE namespace = ?
  AND name = ?;"""
        self._delete_outdated()
        return self.conn.execute(sql, (namespace, name,)).fetchone() is not None

    def get_experiments(self, namespace: str) -> typing.List[typing.Dict]:
        sql = """SELECT name, params, metrics, created_at as time
FROM experiments
WHERE namespace = ?
  AND expires_at IS NULL;"""
        for name, params, metrics, ts in self.conn.execute(sql, (namespace,)):
            yield name, params, metrics, datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')

    def revoke_token(self, token: str):
        sql = """UPDATE tokens
SET expires_at=datetime('now')
WHERE expires_at IS NULL
  AND token = ?;"""
        with self.conn:
            self.conn.execute(sql, (token,))

    def create_token(self, token: str) -> bool:
        sql = """INSERT INTO tokens(token) VALUES (?);"""
        try:
            with self.conn:
                self.conn.execute(sql, (token,))
            return True
        except sqlite3.IntegrityError:
            return False

    def grant_permission(self, token: str, namespace: str) -> bool:
        sql = """INSERT INTO token_collection(token, namespace)
VALUES ((SELECT id FROM tokens WHERE tokens.token = ?), ?);"""
        try:
            with self.conn:
                self.conn.execute(sql, (token, namespace))
            return True
        except sqlite3.IntegrityError:
            return False
