"""Модуль формирующий интерфейс телеграм-бота."""

from data import Commands
from telebot.types import KeyboardButton, ReplyKeyboardMarkup


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
            KeyboardButton(Commands.START_LEARNING),
            KeyboardButton(Commands.EXIT),
        )


class WordsKeyboard(BaseKeyboard):

    def __init__(self, words):
        """Инициализация класса KeyboardBot."""
        super().__init__(row_width=2)
        self._add_words_to_kb(words)

    def _add_words_to_kb(self, words: list[str]):
        word_buttons = [KeyboardButton(word) for word in words]
        self.keyboard.add(word_buttons).row(
            KeyboardButton(Commands.DELETE_WORD),
            KeyboardButton(Commands.ADD_WORD),
            KeyboardButton(Commands.NEXT),
        ).add(KeyboardButton(Commands.MAIN_MENU))
