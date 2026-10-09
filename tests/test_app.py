import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import app
from database import initialize_database


class SqlWorkspaceApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "test.db"
        app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret",
            DATABASE=str(database_path),
            INITIALIZED_DATABASES=set(),
        )
        self.client = app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_guest_can_create_and_update_sql_records(self):
        group_response = self.client.post(
            "/api/data/groups",
            json={"id": "group-1", "name": "Home", "parentId": None},
        )
        self.assertEqual(group_response.status_code, 201)

        task_response = self.client.post(
            "/api/data/tasks",
            json={
                "id": "task-1",
                "groupId": "group-1",
                "name": "Paint",
                "description": "Living room",
                "maxPrice": 200,
                "currentPrice": 25,
                "isComplete": False,
            },
        )
        self.assertEqual(task_response.status_code, 201)

        update_response = self.client.put(
            "/api/data/tasks/task-1",
            json={
                "name": "Paint living room",
                "description": "Walls",
                "maxPrice": 220,
                "currentPrice": 50,
                "isComplete": True,
            },
        )
        self.assertEqual(update_response.status_code, 200)

        workspace = self.client.get("/api/data").get_json()
        self.assertEqual(workspace["groups"], [
            {"id": "group-1", "name": "Home", "parentId": None}
        ])
        self.assertEqual(workspace["tasks"][0]["name"], "Paint living room")
        self.assertEqual(workspace["tasks"][0]["currentPrice"], 50)
        self.assertIs(workspace["tasks"][0]["isComplete"], True)

    def test_guest_data_is_scoped_to_its_session(self):
        self.client.post(
            "/api/data/groups",
            json={"id": "private-group", "name": "Private", "parentId": None},
        )

        other_guest = app.test_client()
        workspace = other_guest.get("/api/data").get_json()
        self.assertEqual(workspace["groups"], [])
        self.assertEqual(workspace["tasks"], [])

    def test_local_storage_import_preserves_legacy_task_fields(self):
        response = self.client.post(
            "/api/data/import-local",
            data=json.dumps(
                {
                    "groups": [
                        {"id": "legacy-group", "name": "Travel", "parentId": None}
                    ],
                    "tasks": [
                        {
                            "id": "legacy-task",
                            "groupId": "legacy-group",
                            "name": "Flights",
                            "description": "Summer trip",
                            "maxPrice": 800,
                            "currentPrice": 300,
                            "isGroup": True,
                        }
                    ],
                    "theme": "dark",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        workspace = self.client.get("/api/data").get_json()
        self.assertEqual(workspace["theme"], "dark")
        self.assertTrue(workspace["tasks"][0]["isComplete"])

    def test_account_data_is_scoped_and_password_is_verified(self):
        account_response = self.client.post(
            "/api/auth/create-acc",
            json={
                "name": "Alex",
                "email": "alex@example.com",
                "password": "correct horse",
            },
        )
        self.assertEqual(account_response.status_code, 201)
        self.client.post(
            "/api/data/groups",
            json={"id": "account-group", "name": "Account", "parentId": None},
        )

        another_client = app.test_client()
        login_response = another_client.post(
            "/api/auth/login",
            json={"email": "ALEX@example.com", "password": "correct horse"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(
            another_client.get("/api/details/user-details").get_json()[
                "isAuthenticated"
            ]
        )
        self.assertEqual(
            [group["id"] for group in another_client.get("/api/data").get_json()["groups"]],
            ["account-group"],
        )
        self.assertEqual(
            another_client.post("/api/auth/logout").status_code,
            200,
        )
        self.assertFalse(
            another_client.get("/api/details/user-details").get_json()[
                "isAuthenticated"
            ]
        )
        self.assertEqual(
            another_client.get("/api/data").get_json()["groups"],
            [],
        )
        self.assertEqual(
            another_client.post(
                "/api/auth/login",
                json={"email": "alex@example.com", "password": "wrong password"},
            ).status_code,
            401,
        )

    def test_rejects_invalid_amounts_and_missing_group(self):
        response = self.client.post(
            "/api/data/tasks",
            json={
                "id": "invalid",
                "groupId": "missing",
                "name": "Task",
                "description": "",
                "maxPrice": -1,
                "currentPrice": 0,
                "isComplete": False,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_replaces_empty_legacy_groups_table(self):
        database_path = Path(app.config["DATABASE"])
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                'CREATE TABLE "Groups" ('
                '"id" INTEGER PRIMARY KEY, "name" TEXT NOT NULL, '
                '"parent_id" TEXT NOT NULL)'
            )

        initialize_database(database_path)
        response = self.client.post(
            "/api/data/groups",
            json={"id": "migrated-group", "name": "Home", "parentId": None},
        )
        self.assertEqual(response.status_code, 201)

    def test_does_not_replace_nonempty_legacy_groups_table(self):
        database_path = Path(app.config["DATABASE"])
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                'CREATE TABLE "Groups" ('
                '"id" INTEGER PRIMARY KEY, "name" TEXT NOT NULL, '
                '"parent_id" TEXT NOT NULL)'
            )
            connection.execute(
                'INSERT INTO "Groups" ("name", "parent_id") VALUES (?, ?)',
                ("Preserve me", ""),
            )

        with self.assertRaisesRegex(RuntimeError, "contains data"):
            initialize_database(database_path)


if __name__ == "__main__":
    unittest.main()
