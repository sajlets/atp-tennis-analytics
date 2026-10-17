from pathlib import Path

import duckdb
import pytest

DB_PATH = Path("data/chinook.duckdb")


@pytest.fixture
def con():
    if not DB_PATH.exists():
        pytest.skip("database not built; run: make load && make sql")
    connection = duckdb.connect(str(DB_PATH), read_only=True)
    yield connection
    connection.close()


def test_all_quality_checks_pass(con):
    failed = con.execute(
        "SELECT check_name FROM quality_report WHERE status = 'FAIL'"
    ).fetchall()
    assert failed == []


def test_kpi_revenue_adds_up_to_invoice_total(con):
    invoice_total = con.execute("SELECT sum(total) FROM stg_invoice").fetchone()[0]
    for view in ["kpi_revenue_by_year", "kpi_revenue_by_genre", "kpi_revenue_by_artist"]:
        kpi_total = con.execute(f"SELECT sum(revenue) FROM {view}").fetchone()[0]
        assert kpi_total == invoice_total, f"{view} does not add up to the invoice total"