import pytest
from sqlalchemy import inspect


@pytest.mark.asyncio
async def test_migration_tables_exist(test_engine):
    """All tables should be created (doctors, patients, vitals)."""
    async with test_engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

    assert "doctors" in tables
    assert "patients" in tables
    assert "vitals" in tables
