import asyncpg
import datetime
import pytz
from typing import List, Optional

from config import config
from utils import format_datetime, refactor_category, reverse_refactor_category


class Database:
    pool: asyncpg.Pool = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(dsn=str(config.postgres_dsn))
            print("Successfully connected to PostgreSQL")

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("PostgreSQL connection pool closed")

    async def add_user(self, tg_id: int, tg_nick: str = None) -> bool:
        sql = "INSERT INTO users (tg_id, tg_nick) VALUES ($1, $2) ON CONFLICT (tg_id) DO NOTHING"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, tg_id, tg_nick)
            return 'INSERT 0 1' in result

    async def add_transaction(self, tg_id: int, category: str, summ: float) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    sql_insert = "INSERT INTO transactions (tg_id, category, summ, date) VALUES ($1, $2, $3, $4)"
                    utc_now = datetime.datetime.now(pytz.utc)
                    await conn.execute(sql_insert, tg_id, refactor_category(category), summ, utc_now)

                    await self._update_user_summ(tg_id, refactor_category(category), summ, conn=conn)
                    return True
                except Exception as e:
                    print(f"Ошибка при добавлении транзакции: {e}")
                    return False

    async def _update_user_summ(self, tg_id: int, category: str, summ: float, conn: asyncpg.Connection):
        sql_update = f"UPDATE users SET {category} = {category} + $1, summ = summ + $1 WHERE tg_id = $2"
        await conn.execute(sql_update, summ, tg_id)

    async def get_user_data(self, tg_id: int) -> Optional[asyncpg.Record]:
        sql = "SELECT * FROM users WHERE tg_id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, tg_id)

    async def get_user_transactions(self, tg_id: int) -> List[asyncpg.Record]:
        sql = "SELECT * FROM transactions WHERE tg_id = $1 ORDER BY date DESC"
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, tg_id)

    async def get_transaction_by_id(self, transaction_id: int) -> Optional[str]:
        sql = "SELECT * FROM transactions WHERE id = $1"
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(sql, transaction_id)
            if not record:
                return None

            summ = record['summ']
            category = reverse_refactor_category(record['category'])
            date_str = format_datetime(record['date'])
            return f'<b>{summ} ₽</b> | {category} | {date_str}'

    async def delete_transaction_by_id(self, transaction_id: int) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    sql_select = "SELECT tg_id, category, summ, date FROM transactions WHERE id = $1"
                    tr_data = await conn.fetchrow(sql_select, transaction_id)
                    if not tr_data:
                        return False

                    tg_id, category, summ, date = tr_data

                    sql_archive = "INSERT INTO deleted_transactions (id, tg_id, category, summ, date, delete_date) VALUES ($1, $2, $3, $4, $5, $6)"
                    await conn.execute(sql_archive, transaction_id, tg_id, category, summ, date,
                                       datetime.datetime.now(pytz.utc))

                    await self._update_user_summ(tg_id, category, -summ, conn=conn)

                    await conn.execute("DELETE FROM transactions WHERE id = $1", transaction_id)
                    return True
                except Exception as e:
                    print(f"Ошибка при удалении транзакции: {e}")
                    return False

    async def get_total_summ(self) -> str:
        sql = "SELECT SUM(summ) FROM users"
        async with self.pool.acquire() as conn:
            total_summ = await conn.fetchval(sql)
            return str(total_summ) if total_summ is not None else '0'

    async def fetch_all_from_table(self, table_name: str) -> tuple[list[str], list[asyncpg.Record]] | tuple[None, None]:
        if table_name not in ['users', 'transactions', 'deleted_transactions']:
            raise ValueError("Invalid table name")

        query = f"SELECT * FROM {table_name}"
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query)
            if not records:
                return None, None

            headers = list(records[0].keys())
            return headers, records
