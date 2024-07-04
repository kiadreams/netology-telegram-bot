import os

from telebot import TeleBot
from telebot.types import Message

from database.db_model import DbModel
from model.bot_model import BotModel
from model.data import Commands


bot = TeleBot(os.environ["TOKEN_KIARA_BOT"], skip_pending=True)
root_user_id = 843771109  # from_user.id
db = DbModel(
    login=os.environ["LOGIN_DB"],
    password=os.environ["PASSWORD_DB"],
    db_name="tg_bot_db",
)
chats = {}


@bot.message_handler(commands=Commands.all_commands())
def action_of_command(message: Message):
    """Функция обработки команд бота.

    На вход принимает один параметр:
    :param message: объект типа message
    :return: ничего не возвращает
    """
    user_id = message.from_user.id
    chat = chats.setdefault(
        message.chat.id,
        BotModel(bot, chats, user_id, db),
    )
    chat.action_handler(message)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def action_of_button(message: Message):
    """Функция обработки текстовых сообщений бота.

    На вход принимает один параметр:
    :param message: объект типа message
    :return: ничего не возвращает
    """
    model = chats.get(message.chat.id)
    if model is not None:
        model.action_handler(message)


if __name__ == "__main__":
    print("bot is working...")
    bot.polling()
