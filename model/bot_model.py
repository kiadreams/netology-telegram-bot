from telebot import TeleBot

from database.db_model import DbModel
from model.dictionary import Dictionary
from view.main_menu import MainMenu


class Actions:
    """The class describes the options for the bot's actions."""

    def __init__(self):
        """Set a dictionary of possible actions."""
        self.actions = {}
        self.another_action = None

    @property
    def actions(self) -> dict:
        return self._actions

    @actions.setter
    def actions(self, new_actions):
        self.another_action = None
        self._actions = new_actions

    def action_handler(self, message):
        action = self._actions.get(message.text, None)
        if action is not None:
            action(message)
        elif self.another_action is not None:
            self.another_action(message)

    def add_actions(self, new_actions):
        self._actions.update(new_actions)


class BotModel(Actions):
    """The class describes the functional model of the bot."""

    def __init__(
        self,
        bot: TeleBot,
        chats: dict,
        user_id: int,
        db_model: DbModel,
    ):
        """Set model parameters."""
        Actions.__init__(self)
        self.user_id = user_id
        self.bot = bot
        self.chats = chats
        self.db = db_model
        self.dictionary = Dictionary(self)
        self.__main_menu = MainMenu(self)
        self.actions = self.__main_menu.cmd_actions

    @property
    def bot_name(self):
        return self.bot.get_my_name().name

    def btn_return_to_main_menu(self, message):
        """Return to the main menu of the bot."""
        self.bot.send_message(
            message.chat.id,
            "OK",
            reply_markup=self.__main_menu.keyboard,
        )
        self.actions = self.__main_menu.main_menu_actions

    def btn_start_english_learning(self, message):
        """Start learning English words."""
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        self.dictionary.download_user_words(self.user_id, first_name, last_name)
        self.dictionary.show_curr_word(message)
