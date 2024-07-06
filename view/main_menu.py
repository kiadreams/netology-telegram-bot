from model.data import Buttons, Commands
from view.keyboards import MainMenuKeyboard


class MainMenu(MainMenuKeyboard):
    """A class describing the main menu of the bot."""

    def __init__(self, model):
        """Set button parameters and types of actions in the main menu.

        :param model: link to the bot model
        """
        super().__init__()
        self.bot_model = model
        self.button_actions = {
            Buttons.START_LEARNING: self.bot_model.btn_start_english_learning,
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
        """Start a dialogue with the bot.

        :param message: an object of the Message type
        :return:
        """
        self.bot_model.bot.send_message(
            message.chat.id,
            f"Привет я {self.bot_model.bot_name}! Чем могу помочь?\n\n"
            "(для получения справки по общению со мной в данном меню "
            "введите команду '/help')",
            reply_markup=self.keyboard,
        )
        self.bot_model.actions = self.main_menu_actions

    def btn_finish_bot_chat(self, message):
        """End the dialogue with the bot.

        :param message: an object of the Message type
        :return:
        """
        self.bot_model.bot.send_message(
            message.chat.id,
            "Я ушёл..., но на связи! Хотите продолжить",
            reply_markup=self.delete_keyboard(),
        )

    def exit_from_bot(self, message):
        """Shut down the bot.

        :param message: an object of the Message type
        :return:
        """
        name = message.from_user.first_name
        for chat_id in self.bot_model.chats:
            self.bot_model.bot.send_message(
                chat_id,
                f"Пользователь {name} отключил(а) бота...",
                reply_markup=self.delete_keyboard(),
            )
        self.bot_model.bot.stop_bot()

    def cmd_bot_help(self, message):
        """Show supported commands.

        :param message: an object of the Message type
        :return:
        """
        self.bot_model.bot.send_message(
            message.chat.id,
            text="Бот поддерживает 3 команды - все в нижнем регистре:\n"
            "1) /start - предназначена для входа в главное меню бота любым "
                 "пользователем;\n"
            "2) /exit - нужна для остановки работы бота его администратором "
            "(пока данная команда работае с любым пользователем);\n"
            "3) /help - выводит данное сообщение.\n"
            "В нормальном режиме, для большинства пользователей, навигация "
            "по меню бота осуществляется с использованием кнопок "
            "клавиатуры, сами команды работают только в главном меню "
            "бота.\n\n(Чтобы начать чат с ботом введите команду '/start')",
            reply_markup=self.delete_keyboard(),
        )
