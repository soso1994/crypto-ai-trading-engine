# Generic feed adapter helpers
# server/src/feeds/adapter.py
import asyncio
import logging
from typing import Callable

LOGGER = logging.getLogger("datafeeds.adapter")

async def file_writer_factory(path: str):
    # returns async writer that appends JSON lines to path
    async def writer(msg):
        loop = asyncio.get_event_loop()
        line = (str(msg) + "\n").encode("utf-8")
        await loop.run_in_executor(None, lambda: open(path, "ab").write(line))
    return writer

async def db_writer_factory(db_pool, table_name: str):
    # placeholder for producing an async writer that inserts into Postgres
    async def writer(msg):
        async with db_pool.acquire() as conn:
            # implement insert logic per schema
            await conn.execute("-- INSERT STATEMENT --")
    return writer
