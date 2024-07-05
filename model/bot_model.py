from telebot import TeleBot

from model.dictionary import Dictionary
from view.main_menu import MainMenu
from database.db_model import DbModel

class Actions:

    def __init__(self):
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

    def __init__(self, bot: TeleBot, chats: dict, user_id: int, db_model: DbModel):
        """Класс описывающий логику бота."""
        Actions.__init__(self)
        self.user_id = user_id
        self.bot = bot
        self.name = bot.get_my_name().name
        self.chats = chats
        self.db = db_model
        self.main_menu = MainMenu(self)
        self.dictionary = Dictionary(self, user_id)
        self.actions = self.main_menu.cmd_actions

    def btn_return_to_main_menu(self, message):
        self.bot.send_message(
            message.chat.id,
            "OK",
            reply_markup=self.main_menu.keyboard,
        )
        self.actions = self.main_menu.main_menu_actions

    def btn_start_english_learning(self, message):
        self.dictionary.load_words_from_db(self.user_id)
        self.dictionary.show_curr_word(message)
