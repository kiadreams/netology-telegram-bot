"""Модуль формирующий интерфейс телеграм-бота."""

from enum import StrEnum

from telebot import types


class Commands(StrEnum):
    BYE_BOT = "Передумал - пока бот"
    START_LEARNING = "Изучение английских слов..."
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово🔙"
    NEXT = "Дальше ⏭"


def get_buttons(*args) -> list[types.KeyboardButton]:
    """Функция получения кнопок.

    На вход принимает список названий кнопок
    :param args: список названий кнопок
    :return:
    """
    return [types.KeyboardButton(text) for text in args]


class KeyboardBot:
    """Класс описывающий клавиатуру телеграмм бота."""

    word_buttons = (Commands.ADD_WORD, Commands.DELETE_WORD, Commands.NEXT)
    start_buttons = (Commands.START_LEARNING, Commands.BYE_BOT)

    def __init__(self, row_width=2):
        """Инициализация класса KeyboardBot."""
        self._kb = types.ReplyKeyboardMarkup(row_width=row_width)

    @property
    def kb(self):
        """Возвращает клавиатуру.

        :return:
        """
        return self._kb

    def load_btn_for_start_kb(self):
        start_buttons = get_buttons(*KeyboardBot.start_buttons)
        self._kb.add(*start_buttons)

    def load_btn_for_learning_kb(self):
        learning_buttons = get_buttons(
            *KeyboardBot.word_buttons,
            Commands.BYE_BOT,
        )
        self._kb.add(*learning_buttons)
