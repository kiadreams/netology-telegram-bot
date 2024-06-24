"""Модуль формирующий интерфейс телеграм-бота."""

from enum import StrEnum

from telebot import types
from data_bot import Commands


# def get_buttons(*args) -> list[types.KeyboardButton]:
#     """Функция получения кнопок.
#
#     На вход принимает список названий кнопок
#     :param args: список названий кнопок
#     :return:
#     """
#     return [types.KeyboardButton(text) for text in args]




class KeyboardBot:
    """Класс описывающий клавиатуру телеграмм бота."""

    def __init__(self, row_width=2):
        """Инициализация класса KeyboardBot."""
        self._kb = types.ReplyKeyboardMarkup(
            row_width=row_width,
            resize_keyboard=True,
        )

    @property
    def kb(self):
        """Возвращает клавиатуру.

        :return:
        """
        return self._kb

    def load_btn_for_start_kb(self):
        start_buttons = get_buttons(Commands.START_LEARNING, Commands.EXIT)
        self._kb.add(*start_buttons)

    def load_btn_for_learning_kb(self):
        btn_next_word = types.KeyboardButton(Commands.NEXT)
        btn_add_word = types.KeyboardButton(Commands.ADD_WORD)
        btn_delete_word = types.KeyboardButton(Commands.DELETE_WORD)
        btn_
        self._kb.add(*learning_buttons)
