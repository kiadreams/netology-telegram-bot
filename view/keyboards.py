from telebot import types

from model.data import Buttons


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
        self._kb = types.ReplyKeyboardMarkup(
            row_width=row_width,
            resize_keyboard=True,
        )

    @staticmethod
    def delete_keyboard():
        return types.ReplyKeyboardRemove()


class MainMenuKeyboard(BaseKeyboard):
    """Класс описывающий клавиатуру главного меню бота."""

    def __init__(self):
        """Инициализация класса KeyboardBot."""
        super().__init__(row_width=1)
        self.keyboard.add(
            types.KeyboardButton(Buttons.START_LEARNING),
            types.KeyboardButton(Buttons.FINISH_BOT_CHAT),
        )


class DictionaryKeyboard(BaseKeyboard):

    def __init__(self):
        """Инициализация класса KeyboardBot."""
        super().__init__(row_width=2)

    def add_words_to_kb(self, words: list[str]):
        word_buttons = [types.KeyboardButton(word) for word in words]
        return (
            self.keyboard.add(*word_buttons).row(
                types.KeyboardButton(Buttons.DELETE_WORD),
                types.KeyboardButton(Buttons.ADD_WORD),
                types.KeyboardButton(Buttons.NEXT),
            ).add(types.KeyboardButton(Buttons.MAIN_MENU))
        )
