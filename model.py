from telebot.handler_backends import State, StatesGroup
from telebot import TeleBot
import keyboards
from data import Buttons, Commands
from telebot.types import Message


class BotStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()


class Actions:

    def __init__(self):
        self.actions = {}

    @property
    def actions(self) -> dict:
        return self._actions

    @actions.setter
    def actions(self, new_actions):
        self._actions = new_actions

    def action_handler(self, message):
        action = self._actions.get(message.text, None)
        if action is not None:
            action(message)

    def add_actions(self, new_actions):
        self._actions.update(new_actions)


class CommandHandler(Actions):

    def __init__(self):
        super().__init__()
        self.cmd_actions = {
            f"/{Commands.START}": self.cmd_start_bot_chat,
            f"/{Commands.EXIT}": self.exit_from_bot,
            f"/{Commands.HELP}": self.cmd_bot_help,
        }

    def cmd_start_bot_chat(self, message): ...

    def exit_from_bot(self, message): ...

    def cmd_bot_help(self, message):
        self.bot.send_message(
            message.chat.id,
            "Моя помощь ещё в стадии разработки...",
            reply_markup=keyboards.StartKeyboard().keyboard,
        )


class MainMenuActionsMixin:

    def __init__(self):
        self.main_menu_actions = {
            Buttons.START_LEARNING: self.btn_start_english_learning,
            Buttons.FINISH_BOT_CHAT: self.btn_finish_bot_chat,
        }

    def btn_finish_bot_chat(self, message):
        self.bot.send_message(
            message.chat.id,
            "Я ушёл...",
            reply_markup=keyboards.StartKeyboard.delete_keyboard(),
        )

    def btn_start_english_learning(self, message): ...


class WordMenuActionsMixin:

    def __init__(self):
        self.english_word_menu_actions = {
            Buttons.NEXT: self.btn_show_next_word,
            Buttons.DELETE_WORD: self.btn_deleting_word_from_dict,
            Buttons.ADD_WORD: self.bnt_add_word_to_dict,
            Buttons.MAIN_MENU: self.btn_return_to_main_menu,
        }

    def btn_show_next_word(self, message): ...

    def bnt_add_word_to_dict(self, message): ...

    def btn_deleting_word_from_dict(self, message): ...

    def btn_return_to_main_menu(self, message): ...


class ButtonHandler(Actions, MainMenuActionsMixin, WordMenuActionsMixin):

    def __init__(self):
        super().__init__()
        MainMenuActionsMixin.__init__(self)
        WordMenuActionsMixin.__init__(self)


class BotModel(CommandHandler, ButtonHandler):

    def __init__(self, bot: TeleBot, chats: dict):
        """Класс описывающий логику бота."""
        Actions.__init__(self)
        CommandHandler.__init__(self)
        ButtonHandler.__init__(self)
        self.bot = bot
        self.name = bot.get_my_name().name
        self.chats = chats
        self.actions = self.cmd_actions

    def cmd_start_bot_chat(self, message):
        self.bot.send_message(
            message.chat.id,
            f"Привет я {self.name}! Чем помочь?",
            reply_markup=keyboards.StartKeyboard().keyboard,
        )
        self.actions = self.main_menu_actions
        self.add_actions(self.cmd_actions)

    def btn_return_to_main_menu(self, message):
        self.bot.send_message(
            message.chat.id,
            "OK",
            reply_markup=keyboards.StartKeyboard().keyboard,
        )
        self.actions = self.main_menu_actions
        self.add_actions(self.cmd_actions)

    def btn_start_english_learning(self, message):
        english_word = "end"
        self.bot.send_message(
            message.chat.id,
            f"Выберите перевод слова: {english_word}",
            reply_markup=keyboards.WordsKeyboard([english_word]).keyboard,
        )
        self.actions = self.english_word_menu_actions

    def exit_from_bot(self, message: Message):
        name = message.from_user.first_name
        for chat_id in self.chats:
            self.bot.send_message(
                chat_id,
                f"Пользователь {name} отключил(а) бот...",
                reply_markup=keyboards.StartKeyboard.delete_keyboard(),
            )
        self.bot.stop_bot()

