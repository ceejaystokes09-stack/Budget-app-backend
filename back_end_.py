import os
import sqlite3 as sql
import tkinter as tk
from contextlib import closing
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple, Union

from werkzeug.security import check_password_hash, generate_password_hash


class backend:
    """Provide generic SQLite helpers for a single configured table."""

    def __init__(
        self,
        table_name: str = "users",
        db_folder_name: str = "db",
        db_file_name: str = "db.db",
        **kwargs: Any,
    ) -> None:
        """Set the table, database location, and optional row fields."""
        self.__dir_path: str = os.path.dirname(os.path.abspath(__file__))
        db_dir: str = os.path.join(self.__dir_path, db_folder_name)
        os.makedirs(db_dir, exist_ok=True)

        self.__db_path: str = os.path.join(db_dir, db_file_name)
        self.table_name: str = table_name
        self.data_fields: Dict[str, Any] = kwargs
        for key, value in kwargs.items():
            setattr(self, f"_{key}", value)

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """Quote a SQLite table or column name so it cannot alter a query."""
        if not identifier or "\x00" in identifier:
            raise ValueError(
                "SQL identifiers must be non-empty and contain no NUL."
            )
        return '"' + identifier.replace('"', '""') + '"'

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a Werkzeug password hash suitable for database storage."""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Check a plain-text password against a stored Werkzeug hash."""
        return check_password_hash(password_hash, password)

    def add_to_db(self, primary_key: Optional[str] = None) -> bool:
        """Insert initialization fields and report success."""
        if not self.data_fields:
            return False

        columns: str = ", ".join(
            self._quote_identifier(column) for column in self.data_fields
        )
        placeholders: str = ", ".join("?" for _ in self.data_fields)
        values: Tuple[Any, ...] = tuple(self.data_fields.values())
        query: str = (
            f"INSERT INTO {self._quote_identifier(self.table_name)} "
            f"({columns}) VALUES ({placeholders})"
        )

        try:
            with closing(sql.connect(self.__db_path)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(query, values)
                connection.commit()
            return True
        except sql.Error:
            return False

    def clear_db(self) -> bool:
        """Delete every row from the configured table and report success."""
        query: str = f"DELETE FROM {self._quote_identifier(self.table_name)}"
        try:
            with closing(sql.connect(self.__db_path)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(query)
                connection.commit()
            return True
        except sql.Error:
            return False

    def delete_user_from_db(self, column_name: str, value: Any) -> bool:
        """Delete rows whose selected column matches the supplied value."""
        query: str = (
            f"DELETE FROM {self._quote_identifier(self.table_name)} "
            f"WHERE {self._quote_identifier(column_name)} = ?"
        )
        try:
            with closing(sql.connect(self.__db_path)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(query, (value,))
                connection.commit()
            return True
        except sql.Error:
            return False

    def update_data(
        self,
        update_column: str,
        new_value: Any,
        search_column: str,
        search_value: Any,
    ) -> bool:
        """Update a column for rows matching the supplied search condition."""
        query: str = (
            f"UPDATE {self._quote_identifier(self.table_name)} "
            f"SET {self._quote_identifier(update_column)} = ? "
            f"WHERE {self._quote_identifier(search_column)} = ?"
        )
        try:
            with closing(sql.connect(self.__db_path)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(query, (new_value, search_value))
                connection.commit()
            return True
        except sql.Error:
            return False

    def get_columns(self) -> List[str]:
        """Return the configured table's column names in schema order."""
        query: str = (
            f"PRAGMA table_info({self._quote_identifier(self.table_name)})"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query)
                return [row[1] for row in cursor.fetchall()]

    def get_all_data(
        self,
    ) -> List[Tuple[Optional[Union[int, float, str, bytes]], ...]]:
        """Return every row from the configured table."""
        query: str = (
            f"SELECT * FROM {self._quote_identifier(self.table_name)}"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def count_rows(self) -> int:
        """Return the number of rows stored in the configured table."""
        query: str = (
            f"SELECT COUNT(*) FROM {self._quote_identifier(self.table_name)}"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query)
                result: Optional[Tuple[int]] = cursor.fetchone()
        return result[0] if result is not None else 0

    def table_exists(self) -> bool:
        """Check whether the configured table exists in the database."""
        query: str = (
            "SELECT 1 FROM sqlite_master WHERE type = 'table' "
            "AND name = ? LIMIT 1"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query, (self.table_name,))
                return cursor.fetchone() is not None

    def show_db(self) -> None:
        """Display the table's rows in a Tkinter Treeview window."""
        try:
            columns: List[str] = self.get_columns()
            rows = self.get_all_data()
        except sql.Error:
            return
        if not columns:
            return

        root: tk.Tk = tk.Tk()
        root.title(f"Database Viewer - {self.table_name}")
        root.geometry("800x400")
        table: ttk.Treeview = ttk.Treeview(
            root, columns=columns, show="headings"
        )

        for column in columns:
            table.heading(column, text=column)
            table.column(column, width=120, anchor="center")
        for row in rows:
            table.insert("", tk.END, values=row)

        scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            root, orient="vertical", command=table.yview
        )
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")
        root.mainloop()

    def data_exists(self, column: str, data_to_check: Any) -> bool:
        """Check if any row has the value in the selected column."""
        query: str = (
            f"SELECT 1 FROM {self._quote_identifier(self.table_name)} "
            f"WHERE {self._quote_identifier(column)} = ? LIMIT 1"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query, (data_to_check,))
                return cursor.fetchone() is not None

    def verify_user(
        self,
        email_column: str = "Email",
        password_column: str = "Password",
    ) -> bool:
        """Verify initialization credentials against a saved password hash."""
        email: Any = self.data_fields.get(email_column)
        password: Any = self.data_fields.get(password_column)
        if (
            not isinstance(email, str)
            or not isinstance(password, str)
        ):
            return False

        query: str = (
            f"SELECT {self._quote_identifier(password_column)} "
            f"FROM {self._quote_identifier(self.table_name)} "
            f"WHERE {self._quote_identifier(email_column)} = ?"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query, (email,))
                user: Optional[Tuple[Any, ...]] = cursor.fetchone()

        stored_hash: Any = user[0] if user else None
        return isinstance(stored_hash, str) and self.verify_password(
            stored_hash, password
        )

    def get_data_(
        self,
        target_column: str,
        search_column: str,
        search_value: Any,
    ) -> Optional[Union[int, float, str, bytes]]:
        """Return one selected value for the first row matching the search."""
        query: str = (
            f"SELECT {self._quote_identifier(target_column)} "
            f"FROM {self._quote_identifier(self.table_name)} "
            f"WHERE {self._quote_identifier(search_column)} = ?"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query, (search_value,))
                result: Optional[Tuple[Any, ...]] = cursor.fetchone()
        return result[0] if result else None

    def get_data_by_conditions(
        self,
        target_column: str,
        conditions: Dict[str, Any],
    ) -> Optional[Union[int, float, str, bytes]]:
        """Return a field from a row matching every supplied column condition.

        Pass any number of ``column: value`` pairs in ``conditions``.
        ``None`` values match SQL NULL. An empty mapping returns ``None``.
        """
        if not conditions:
            return None

        where_clauses: List[str] = []
        values: List[Any] = []
        for column, value in conditions.items():
            quoted_column: str = self._quote_identifier(column)
            if value is None:
                where_clauses.append(f"{quoted_column} IS NULL")
            else:
                where_clauses.append(f"{quoted_column} = ?")
                values.append(value)

        query: str = (
            f"SELECT {self._quote_identifier(target_column)} "
            f"FROM {self._quote_identifier(self.table_name)} "
            f"WHERE {' AND '.join(where_clauses)} LIMIT 1"
        )
        with closing(sql.connect(self.__db_path)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query, tuple(values))
                result: Optional[Tuple[Any, ...]] = cursor.fetchone()
        return result[0] if result else None

    def create_table_safely(self, schema_definition: str) -> bool:
        """Create the configured table using a trusted SQLite schema."""
        query: str = (
            "CREATE TABLE IF NOT EXISTS "
            f"{self._quote_identifier(self.table_name)} "
            f"({schema_definition})"
        )
        try:
            with closing(sql.connect(self.__db_path)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(query)
                connection.commit()
            return True
        except sql.Error:
            return False
