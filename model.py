from telebot import TeleBot
from telebot.handler_backends import State, StatesGroup

from kaira_bot import bot


class BotStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()


class BotModel:

    def __init__(self, bot: TeleBot):
        """Класс описывающий логику бота."""
        self.bot = bot

    @bot.message_handler(commands=["start"])
    def send_welcome(self, message):
        """Функция вывода приветствия бота.

        На вход принимает только один параметр:
        :param message: объект типа message
        :return: ничего не возвращает
        """
        name = self.bot.get_my_name().name
        start_keyboard = KeyboardBot(1)
        start_keyboard.load_btn_for_start_kb()
        bot.send_message(
            message.chat.id,
            f"Привет я {name}! Чем помочь?",
            reply_markup=start_keyboard.kb,
        )

    @bot.message_handler(func=lambda message: True, content_types=["text"])
    def choosing_actions(self, message):
        if message.text == Commands.EXIT:
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
    def send_help(self, message):
        """Функция обрабатывает команду.

        На вход принимает только один параметр:
        :param message: объект типа message
        :return:
        """
        bot.reply_to(message, "Я знаю две команды не полных!")
