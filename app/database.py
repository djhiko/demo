"""Модуль, который хранит в себе подключение к sqlite3 базе данных"""

import sqlite3


def get_conn():
    """Функция для получения соединения к БД"""
    conn = sqlite3.connect("demo.db")
    conn.row_factory = (
        sqlite3.Row
    )  # Это нужно для того, чтобы при выборке sqlite3 отдавал нам словарь, а не кортеж
    return conn
