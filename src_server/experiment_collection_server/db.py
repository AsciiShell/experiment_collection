import sqlite3

from flask import g, current_app

INIT_STATEMENT = """CREATE TABLE IF NOT EXISTS experiments
(
    collection_name text,
    name            text,
    params          text not null,
    metrics         text not null,
    created_at      text not null,
    PRIMARY KEY (collection_name, name)
)"""

INSERT_STATEMENT = """INSERT INTO experiments (collection_name, name, params, metrics, created_at)
VALUES (?, ?, ?, ?, ?)
"""

SELECT_STATEMENT = """SELECT name, params, metrics, created_at as time
FROM experiments
WHERE collection_name = ?"""

DELETE_STATEMENT = """DELETE
FROM experiments
WHERE collection_name = ?
  AND name = ?"""

SELECT_EXISTS_STATEMENT = """SELECT 1
FROM experiments
WHERE collection_name = ?
  AND name = ?"""


class ExperimentDB:
    def __init__(self, path='main.db'):
        self.conn = sqlite3.connect(path)
        with self.conn:
            self.conn.execute(INIT_STATEMENT)

    def close(self):
        self.conn.close()

    def add_experiment(self, collection_name: str, name: str, params: str, metrics: str, time: str):
        with self.conn:
            self.conn.execute(INSERT_STATEMENT, (collection_name, name, params, metrics, time,))

    def delete_experiment(self, collection_name: str, name: str):
        with self.conn:
            self.conn.execute(DELETE_STATEMENT, (collection_name, name,)).fetchone()

    def check_experiment(self, collection_name: str, name: str) -> bool:
        return self.conn.execute(SELECT_EXISTS_STATEMENT, (collection_name, name,)).fetchone() is not None

    def get_experiments(self, collection_name: str):
        return self.conn.execute(SELECT_STATEMENT, (collection_name,)).fetchall()


def get_db():
    if 'db' not in g:
        g.db = ExperimentDB(current_app.config['DB_PATH'])

    return g.db


__all__ = ['ExperimentDB', 'get_db', ]
