from data import Buttons, Commands
from keyboards import MainMenuKeyboard

# from model import BotModel


class MainMenu(MainMenuKeyboard):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.button_actions = {
            Buttons.START_LEARNING: self.model.btn_start_english_learning,
            Buttons.FINISH_BOT_CHAT: self.btn_finish_bot_chat,
        }
        self.cmd_actions = {
            f"/{Commands.START}": self.cmd_start_bot_chat,
            f"/{Commands.EXIT}": self.exit_from_bot,
            f"/{Commands.HELP}": self.cmd_bot_help,
        }

    @property
    def main_menu_actions(self):
        return self.button_actions | self.cmd_actions

    def cmd_start_bot_chat(self, message):
        self.model.bot.send_message(
            message.chat.id,
            f"Привет я {self.model.name}! Чем помочь?",
            reply_markup=self.keyboard,
        )
        self.model.actions = self.main_menu_actions

    def btn_finish_bot_chat(self, message):
        self.model.bot.send_message(
            message.chat.id,
            "Я ушёл...",
            reply_markup=self.delete_keyboard(),
        )

    def exit_from_bot(self, message):
        name = message.from_user.first_name
        for chat_id in self.model.chats:
            self.model.bot.send_message(
                chat_id,
                f"Пользователь {name} отключил(а) бота...",
                reply_markup=self.delete_keyboard(),
            )
        self.model.bot.stop_bot()

    def cmd_bot_help(self, message):
        self.model.bot.send_message(
            message.chat.id,
            "Моя помощь ещё в стадии разработки...",
            reply_markup=self.keyboard,
        )
