import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional, Union


ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = ROOT / "Festival-data" / "DATA.db"
SCHEMA_PATH = ROOT / "schema.sql"


def initialize_database(
    database_path: Optional[Union[str, Path]] = None,
) -> None:
    """Create the application tables and indexes if they do not exist."""
    path = Path(database_path or os.environ.get("BUDGET_DATABASE_PATH", DEFAULT_DATABASE_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(path, timeout=10)) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        try:
            connection.execute("BEGIN IMMEDIATE")
            groups = connection.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE type = 'table' AND name = 'Groups'"
            ).fetchone()
            migration = ""
            if groups:
                columns = {
                    row[1]
                    for row in connection.execute('PRAGMA table_info("Groups")')
                }
                if "OWNER_ID" not in columns:
                    group_count = connection.execute(
                        'SELECT COUNT(*) FROM "Groups"'
                    ).fetchone()[0]
                    task_table = connection.execute(
                        "SELECT 1 FROM sqlite_master "
                        "WHERE type = 'table' AND name = 'Tasks'"
                    ).fetchone()
                    task_count = (
                        connection.execute(
                            'SELECT COUNT(*) FROM "Tasks"'
                        ).fetchone()[0]
                        if task_table
                        else 0
                    )
                    if group_count or task_count:
                        raise RuntimeError(
                            "The legacy Groups table contains data and cannot be "
                            "replaced automatically. Back up DATA.db and migrate "
                            "those rows before starting the application."
                        )
                    migration = (
                        'DROP INDEX IF EXISTS "IX_Groups_Owner_Parent";\n'
                        'DROP INDEX IF EXISTS "IX_Tasks_Owner_Group";\n'
                        'DROP TABLE IF EXISTS "Tasks";\n'
                        'DROP TABLE "Groups";\n'
                    )

            statements = migration + SCHEMA_PATH.read_text(encoding="utf-8")
            statement = ""
            for line in statements.splitlines():
                statement += line + "\n"
                if sqlite3.complete_statement(statement):
                    if statement.strip():
                        connection.execute(statement)
                    statement = ""
            if statement.strip():
                raise RuntimeError("The database schema contains an incomplete SQL statement.")
            connection.commit()
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        connection.execute("PRAGMA foreign_keys = ON")


def connect_database(
    database_path: Optional[Union[str, Path]] = None,
) -> sqlite3.Connection:
    """Open a row-mapped SQLite connection with foreign-key checks enabled."""
    path = Path(database_path or os.environ.get("BUDGET_DATABASE_PATH", DEFAULT_DATABASE_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
