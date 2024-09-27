from datetime import datetime
import aiosqlite
import csv
import asyncio


def format_datetime(input_datetime_str) -> str:
    # Словарь для преобразования номера месяца в его название
    month_names = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'sep',
        10: 'oct',
        11: 'nov',
        12: 'dec'
    }

    # Преобразуем строку с датой и временем в объект datetime
    input_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M:%S')

    # Извлекаем день, месяц и время
    day = input_datetime.day
    month = input_datetime.month
    time = input_datetime.strftime('%H:%M')

    # Форматируем дату и месяц
    formatted_date = f"{day} {month_names[month]}"

    # Возвращаем окончательную строку
    formatted_datetime = f"{formatted_date} в {time}"
    return formatted_datetime


def refactor_category(category):
    if category == '🍟 Mак':
        return 'vit'
    elif category == '🐔 KFC':
        return 'kfc'
    elif category == '🍔 БК':
        return 'bk'
    elif category == '🍕🥦🥞 Другое':
        return 'other'
    else:
        raise ValueError("Недопустимая категория")


def reverse_refactor_category(category):
    if category == 'vit':
        return '🍟 Mак'
    elif category == 'kfc':
        return '🐔 KFC'
    elif category == 'bk':
        return '🍔 БК'
    elif category == 'other':
        return '🍕🥦🥞 Другое'
    else:
        raise ValueError("Недопустимая категория")


async def transactions_to_list(transactions) -> list:
    new_transactions = []
    for transaction in transactions:
        new_transactions.append(
            [transaction[0], reverse_refactor_category(transaction[2]), transaction[3],
             format_datetime(transaction[4])])
    new_transactions.reverse()
    return new_transactions


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


async def transaction_to_inline(transactions) -> list:
    inline_buttons_list = []
    for transaction in transactions:
        inline_buttons_list.append(
            f' {transaction[2]} ₽ |'
            f' {transaction[1]} |'
            f' {transaction[3]}')
    return inline_buttons_list


async def export_table_to_csv(table_name, csv_file_path):
    # Подключение к базе данных
    async with aiosqlite.connect('db.db') as db:
        # Чтение всех данных из таблицы
        async with db.execute(f"SELECT * FROM {table_name}") as cursor:
            # Получаем названия столбцов
            column_names = [description[0] for description in cursor.description]

            # Открытие CSV-файла для записи
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)

                # Запись названий столбцов
                writer.writerow(column_names)

                # Запись строк данных
                async for row in cursor:
                    writer.writerow(row)
