"""Модуль создания телеграм-бота."""

import os

import telebot
from telebot import types
from keyboard import KeyboardBot, Commands


bot = telebot.TeleBot(os.environ["TOKEN_KIARA_BOT"])


@bot.message_handler(commands=["start"])
def send_welcome(message):
    """Функция вывода приветствия бота.

    На вход принимает только один параметр:
    :param message: объект типа message
    :return: ничего не возвращает
    """
    name = bot.get_my_name().name
    start_keyboard = KeyboardBot(1)
    start_keyboard.load_btn_for_start_kb()
    bot.send_message(
        message.chat.id,
        f"Привет я {name}! Чем помочь?",
        reply_markup=start_keyboard.kb,
    )


@bot.message_handler(func=lambda message: True, content_types=["text"])
def choosing_actions(message):
    if message.text == Commands.BYE_BOT:
        bot.send_message(
            message.chat.id,
            "Я ушёл...",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        bot.stop_bot()
    elif message.text == Commands.START_LEARNING:
        learning_kb = KeyboardBot(2)
        learning_kb.load_btn_for_learning_kb()
        bot.send_message(
            message.chat.id,
            "получилось",
            reply_markup=learning_kb.kb,
        )


@bot.message_handler(commands=["help"])
def send_help(message):
    """Функция обрабатывает команду.

    На вход принимает только один параметр:
    :param message: объект типа message
    :return:
    """
    bot.reply_to(message, "Я знаю две команды не полных!")


if __name__ == "__main__":
    print("Bot is running!..")
    bot.polling()
