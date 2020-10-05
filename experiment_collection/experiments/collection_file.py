import sqlite3
import typing

import pandas as pd

from .collection_abc import ExperimentCollectionABC
from .experiment import Experiment
from .utils import postprocess_df

INIT_STATEMENT = """CREATE TABLE IF NOT EXISTS experiments
(
    name          text primary key,
    params        text not null,
    metrics       text not null,
    created_at    text not null
)"""

INSERT_STATEMENT = """INSERT INTO experiments (name, params, metrics, created_at)
VALUES (?, ?, ?, ?)
"""

SELECT_STATEMENT = """SELECT name, params, metrics, created_at as time
FROM experiments"""

DELETE_STATEMENT = """DELETE
FROM experiments
WHERE name = ?"""

SELECT_EXISTS_STATEMENT = """SELECT 1
FROM experiments
WHERE  name = ?"""


class ExperimentCollectionLocal(ExperimentCollectionABC):
    def __init__(self, path='main.db'):
        self.conn = sqlite3.connect(path)
        with self.conn:
            self.conn.execute(INIT_STATEMENT)

    def close(self):
        self.conn.close()

    def add_experiment(self, exp: Experiment, /, ignore_included=False):
        data = exp.dumps()
        try:
            with self.conn:
                self.conn.execute(INSERT_STATEMENT, data)
        except sqlite3.IntegrityError as e:
            if not ignore_included:
                raise e

    def delete_experiment(self, exp: typing.Union[Experiment, str]):
        if isinstance(exp, Experiment):
            exp = exp.name
        with self.conn:
            self.conn.execute(DELETE_STATEMENT, (exp,))

    def check_experiment(self, exp: typing.Union[Experiment, str]) -> bool:
        if isinstance(exp, Experiment):
            exp = exp.name
        return self.conn.execute(SELECT_EXISTS_STATEMENT, (exp,)).fetchone() is not None

    def get_experiments(self, normalize=True):
        df = pd.read_sql(SELECT_STATEMENT, self.conn)
        df = postprocess_df(df, normalize)
        return df
