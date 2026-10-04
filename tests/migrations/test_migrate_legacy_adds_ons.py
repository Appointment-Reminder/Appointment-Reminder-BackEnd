# tests/migrations/test_migrate_legacy_adds_ons.py
"""The legacy adds_ons migration, run for real against an in-memory SQLite database."""
import importlib.util
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

MIGRATION = Path(__file__).parents[2] / "alembic" / "versions" / "a1c0de000006_migrate_legacy_adds_ons.py"


@pytest.fixture(scope="module")
def migration():
    spec = importlib.util.spec_from_file_location("migrate_legacy_adds_ons", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def conn():
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(sa.text(
            "CREATE TABLE appointments (id INTEGER PRIMARY KEY, client TEXT, adds_ons VARCHAR)"))
        connection.execute(sa.text(
            "CREATE TABLE unresolved_addon (id INTEGER PRIMARY KEY AUTOINCREMENT, appointment_id INTEGER NOT NULL, "
            "raw_label VARCHAR NOT NULL, resolved_addon_id INTEGER, resolved_at DATETIME, created_at DATETIME)"))
        yield connection


def _run(conn, fn):
    with Operations.context(MigrationContext.configure(conn)):
        fn()


def _labels(conn):
    rows = conn.execute(sa.text("SELECT appointment_id, raw_label FROM unresolved_addon ORDER BY id")).all()
    grouped = {}
    for appointment_id, label in rows:
        grouped.setdefault(appointment_id, []).append(label)
    return grouped


def _insert(conn, rows):
    for id, adds_ons in rows:
        conn.execute(sa.text("INSERT INTO appointments (id, client, adds_ons) VALUES (:id, 'c', :a)"),
                     {"id": id, "a": adds_ons})


class TestSplitLabels:
    @pytest.mark.parametrize("raw", [None, "", "   ", "None", "none", "[]"])
    def test_nothing_to_migrate(self, migration, raw):
        assert migration.split_labels(raw) == []

    def test_a_plain_string_is_one_label(self, migration):
        assert migration.split_labels("10 extra photos, prints") == ["10 extra photos, prints"]

    def test_lines_are_separate_labels(self, migration):
        assert migration.split_labels("Album\r\nPrints\n\nDrone") == ["Album", "Prints", "Drone"]

    def test_json_and_python_list_literals_are_split(self, migration):
        assert migration.split_labels('["Album", "Prints"]') == ["Album", "Prints"]
        assert migration.split_labels("['Album', 'Prints']") == ["Album", "Prints"]

    def test_duplicates_are_kept_once(self, migration):
        assert migration.split_labels("Album\nAlbum") == ["Album"]


class TestUpgrade:
    def test_each_non_empty_value_becomes_unresolved_addons_with_the_raw_label(self, migration, conn):
        _insert(conn, [(1, "Album"), (2, "['Prints', 'Drone']"), (3, "Prints\nAlbum")])

        _run(conn, migration.upgrade)

        assert _labels(conn) == {1: ["Album"], 2: ["Prints", "Drone"], 3: ["Prints", "Album"]}

    def test_null_empty_and_none_values_get_nothing(self, migration, conn):
        _insert(conn, [(1, None), (2, ""), (3, "  "), (4, "None"), (5, "Album")])

        _run(conn, migration.upgrade)

        assert _labels(conn) == {5: ["Album"]}

    def test_migrated_rows_are_still_pending_resolution(self, migration, conn):
        _insert(conn, [(1, "Album")])

        _run(conn, migration.upgrade)

        row = conn.execute(sa.text("SELECT resolved_addon_id, resolved_at, created_at FROM unresolved_addon")).one()
        assert row[0] is None and row[1] is None and row[2] is not None

    def test_the_adds_ons_column_is_gone_and_the_rest_of_the_row_survives(self, migration, conn):
        _insert(conn, [(1, "Album")])

        _run(conn, migration.upgrade)

        columns = [c["name"] for c in sa.inspect(conn).get_columns("appointments")]
        assert "adds_ons" not in columns
        assert conn.execute(sa.text("SELECT id, client FROM appointments")).all() == [(1, "c")]

    def test_downgrade_restores_the_column_with_the_labels(self, migration, conn):
        _insert(conn, [(1, "Album"), (2, "['Prints', 'Drone']"), (3, None)])
        _run(conn, migration.upgrade)

        _run(conn, migration.downgrade)

        restored = dict(conn.execute(sa.text("SELECT id, adds_ons FROM appointments")).all())
        assert restored == {1: "Album", 2: "Prints\nDrone", 3: None}
