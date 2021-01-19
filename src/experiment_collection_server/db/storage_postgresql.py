import datetime
import typing

import psycopg2

from .storage_abc import StorageABC

INIT_STATEMENT = """CREATE TABLE IF NOT EXISTS experiments
(
    namespace  varchar(64),
    name       varchar(64),
    params     text,
    metrics    text,
    created_at timestamp not null,
    expires_at timestamp,
    PRIMARY KEY (namespace, name)
);
CREATE TABLE IF NOT EXISTS tokens
(
    id         SERIAL PRIMARY KEY,
    token      varchar(128) not null UNIQUE,
    created_at timestamp    not null DEFAULT now(),
    expires_at timestamp
);
CREATE TABLE IF NOT EXISTS token_collection
(
    token     integer     not null,
    namespace varchar(64) not null,
    FOREIGN KEY (token) REFERENCES tokens (id),
    PRIMARY KEY (token, namespace)
);"""


class StoragePostgresql(StorageABC):

    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        with self.conn, self.conn.cursor() as curr:
            curr.execute(INIT_STATEMENT)

    def close(self):
        self.conn.close()

    def check_permission(self, token: str, namespace: str) -> bool:
        sql = """SELECT 1
FROM token_collection
         INNER JOIN tokens ON token_collection.token = tokens.id
WHERE tokens.expires_at IS NULL
  AND tokens.token = %s
  AND token_collection.namespace = %s;"""
        with self.conn, self.conn.cursor() as curr:
            curr.execute(sql, (token, namespace,))
            return curr.fetchone() is not None

    def _delete_outdated(self):
        sql = """DELETE
FROM experiments
WHERE expires_at < now(); """
        with self.conn, self.conn.cursor() as curr:
            curr.execute(sql)

    def reserve_experiment(self, namespace: str, name: str, duration: int) -> bool:
        if self.check_experiment(namespace, name):
            return False
        self._delete_outdated()
        sql = """INSERT INTO experiments (namespace, name, created_at, expires_at)
VALUES (%s, %s, now(), now() + interval %s);"""
        try:
            with self.conn, self.conn.cursor() as curr:
                curr.execute(sql, (namespace, name, '{} seconds'.format(duration)))
            return True
        except psycopg2.IntegrityError:
            return False

    # pylint: disable=R0913
    def create_experiment(self, namespace: str, name: str, params: str, metrics: str, time: datetime.datetime) -> bool:
        sql1 = """DELETE
FROM experiments
WHERE expires_at IS NOT NULL
  AND namespace = %s
  AND name = %s"""
        sql2 = """INSERT INTO experiments (namespace, name, params, metrics, created_at)
VALUES (%s, %s, %s, %s, %s);"""
        self._delete_outdated()
        try:
            with self.conn, self.conn.cursor() as curr:
                curr.execute(sql1, (namespace, name,))
                curr.execute(sql2, (namespace, name, params, metrics, time,))
            return True
        except psycopg2.IntegrityError:
            return False

    def delete_experiment(self, namespace: str, name: str):
        sql = """DELETE
FROM experiments
WHERE namespace = %s
  AND name = %s;"""
        self._delete_outdated()
        with self.conn, self.conn.cursor() as curr:
            curr.execute(sql, (namespace, name,))

    def check_experiment(self, namespace: str, name: str) -> bool:
        sql = """SELECT 1
FROM experiments
WHERE namespace = %s
  AND name = %s;"""
        self._delete_outdated()
        with self.conn, self.conn.cursor() as curr:
            curr.execute(sql, (namespace, name,))
            return curr.fetchone() is not None

    def get_experiments(self, namespace: str) -> typing.List[typing.Dict]:
        sql = """SELECT name, params, metrics, created_at as time
FROM experiments
WHERE namespace = %s
  AND expires_at IS NULL;"""
        with self.conn, self.conn.cursor() as curr:
            curr.execute(sql, (namespace,))
            return curr.fetchall()

    def revoke_token(self, token: str):
        sql = """UPDATE tokens
SET expires_at=now()
WHERE expires_at IS NULL
  AND token = %s;"""
        with self.conn, self.conn.cursor() as curr:
            curr.execute(sql, (token,))

    def create_token(self, token: str) -> bool:
        sql = """INSERT INTO tokens(token) VALUES (%s);"""
        try:
            with self.conn, self.conn.cursor() as curr:
                curr.execute(sql, (token,))
            return True
        except psycopg2.IntegrityError:
            return False

    def grant_permission(self, token: str, namespace: str) -> bool:
        sql = """INSERT INTO token_collection(token, namespace)
VALUES ((SELECT id FROM tokens WHERE tokens.token = %s), %s);"""
        try:
            with self.conn, self.conn.cursor() as curr:
                curr.execute(sql, (token, namespace))
            return True
        except psycopg2.IntegrityError:
            return False
