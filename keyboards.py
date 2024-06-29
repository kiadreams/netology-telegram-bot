"""Модуль формирующий интерфейс телеграм-бота."""

from data import Buttons
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove


# def delete_keyboard():
#     return ReplyKeyboardRemove()


class BaseKeyboard:
    """Базовый класс всех клавиатур клавиатуру телеграмм бота."""

    def __init__(self, row_width=2):
        """Инициализация базового класса Keyboard."""
        self.keyboard = row_width

    @property
    def keyboard(self):
        """Возвращает клавиатуру.

        :return:
        """
        return self._kb

    @staticmethod
    def delete_keyboard():
        return ReplyKeyboardRemove()

    @keyboard.setter
    def keyboard(self, row_width):
        self._kb = ReplyKeyboardMarkup(
            row_width=row_width,
            resize_keyboard=True,
        )


class StartKeyboard(BaseKeyboard):
    """Класс описывающий стартовую клавиатуру бота."""

    def __init__(self):
        """Инициализация класса KeyboardBot."""
        super().__init__(row_width=1)
        self.keyboard.add(
            KeyboardButton(Buttons.START_LEARNING),
            KeyboardButton(Buttons.FINISH_BOT_CHAT),
        )


class WordsKeyboard(BaseKeyboard):

    def __init__(self, words: list[str]):
        """Инициализация класса KeyboardBot."""
        super().__init__(row_width=2)
        self._add_words_to_kb(words)

    def _add_words_to_kb(self, words: list[str]):
        word_buttons = [KeyboardButton(word) for word in words]
        self.keyboard.add(*word_buttons).row(
            KeyboardButton(Buttons.DELETE_WORD),
            KeyboardButton(Buttons.ADD_WORD),
            KeyboardButton(Buttons.NEXT),
        ).add(KeyboardButton(Buttons.MAIN_MENU))
