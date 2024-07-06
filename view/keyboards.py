from telebot import types

from model.data import Buttons


class BaseKeyboard:
    """The base class for all keyboards."""

    def __init__(self, row_width=2):
        """Set keyboard parameters."""
        self.keyboard = row_width

    @property
    def keyboard(self):
        """Returns an object of the keyboard type.

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
        """Get an empty keyboard object."""
        return types.ReplyKeyboardRemove()


class MainMenuKeyboard(BaseKeyboard):
    """A class describing the keyboard of the main menu of the bot."""

    def __init__(self):
        """Set the keyboard parameters of the main menu of the bot."""
        super().__init__(row_width=1)
        self.keyboard.add(
            types.KeyboardButton(Buttons.START_LEARNING),
            types.KeyboardButton(Buttons.FINISH_BOT_CHAT),
        )


class DictionaryKeyboard(BaseKeyboard):
    """A class describing the dictionary keyboard."""

    def __init__(self):
        """Set the parameters of the bot's dictionary keyboard."""
        super().__init__(row_width=2)

    def add_words_to_kb(self, words: list[str]):
        """Add buttons with words to the keyboard of the bot's dictionary.

        :param words: a list of words for buttons
        :return:
        """
        word_buttons = [types.KeyboardButton(word) for word in words]
        return (
            self.keyboard.add(*word_buttons).row(
                types.KeyboardButton(Buttons.DELETE_WORD),
                types.KeyboardButton(Buttons.ADD_WORD),
                types.KeyboardButton(Buttons.NEXT),
            ).add(types.KeyboardButton(Buttons.MAIN_MENU))
        )
