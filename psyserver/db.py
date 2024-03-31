from typing import Optional, Tuple
import sqlite3

from pathlib import Path
from psyserver.settings import default_db_path


class SQLite:
    def __init__(self, file: Path):
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.close()


def create_studies_table():
    """Create the studies table."""

    command = """
    CREATE TABLE studies (
        study TEXT PRIMARY KEY,
        count INT DEFAULT 0
    );"""

    with SQLite(default_db_path()) as conn:
        cur = conn.cursor()
        cur.execute(command)
        conn.commit()


def get_increment_study_count_db(study: str) -> Tuple[Optional[int], Optional[str]]:
    """Fetch and increment the study participant count."""
    count = None
    error = None
    with SQLite(default_db_path()) as conn:
        cur = conn.cursor()
        try:
            # get count
            res = cur.execute("SELECT count FROM studies WHERE study=?", (study,))
            item = res.fetchone()

            if item is None:
                # insert study, set to 0
                _set_study_count_cur(study, 0, cur)
                count = 0
            else:
                count = item[0]

        except sqlite3.OperationalError:
            error = "table missing, run 'psyserver init_db'"
        else:
            # update count
            cur.execute("UPDATE studies SET count=? WHERE study=?", (count + 1, study))
            conn.commit()

    return count, error


def _set_study_count_cur(study: str, count: int, cur: sqlite3.Cursor) -> sqlite3.Cursor:
    command = """
    INSERT INTO studies (study, count)
    VALUES (?, ?)
    ON CONFLICT(study) DO UPDATE SET count=?
    """
    return cur.execute(command, (study, count, count))


def set_study_count_db(study: str, count: int) -> Optional[str]:
    """Sets the count for a study.

    Returns
    -------
    error : str | None
        A string describing the error, or None for success.
    """
    error = None
    with SQLite(default_db_path()) as conn:
        cur = conn.cursor()
        try:
            _set_study_count_cur(study, count, cur)
        except sqlite3.OperationalError:
            error = "table missing, run 'psyserver init_db'"
        else:
            conn.commit()
    return error
