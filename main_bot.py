import os

from telebot import TeleBot
from telebot.types import Message

from database.db_model import DbModel
from model.bot_model import BotModel
from model.data import Commands


bot = TeleBot(os.environ["TOKEN_BOT"], skip_pending=True)
db_model = DbModel(
    login=os.environ["LOGIN_DB"],
    password=os.environ["PASSWORD_DB"],
    db_name=os.environ["DB_NAME"],
)
chats = {}


@bot.message_handler(commands=Commands.all_commands())
def action_of_command(message: Message):
    """Bot's command processing function.

    :param message: an object of the Message type
    :return:
    """
    user_id = message.from_user.id
    model = chats.setdefault(
        message.chat.id,
        BotModel(bot, chats, user_id, db_model),
    )
    model.action_handler(message)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def action_of_button(message: Message):
    """Text message processing function.

    :param message: an object of the Message type
    :return:
    """
    model = chats.get(message.chat.id)
    if model is not None:
        model.action_handler(message)


if __name__ == "__main__":
    bot.polling()
