import aiosqlite

from db_methods import get_transactions, reverse_refactor_category, get_transaction_by_id


async def main():
    print(await get_transaction_by_id(373))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
