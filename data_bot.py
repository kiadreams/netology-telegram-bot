from enum import StrEnum

from telebot.types import KeyboardButton


class Commands(StrEnum):
    EXIT = "Отключить бота"
    START_LEARNING = "Изучение английских слов..."
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово🔙"
    NEXT = "Дальше ⏭"
    MAIN_MENU = "Главное меню"


class BaseKeyboard:

    def __init__(self):
        """Базовый класс всех клавиатур, описывающий основные кнопки."""
        self.exit_btn = KeyboardButton(Commands.EXIT)
        self.start_learning_btn = KeyboardButton(Commands.START_LEARNING)
        self.add_word_btn = KeyboardButton(Commands.ADD_WORD)
        self.delete_word_btn = KeyboardButton(Commands.DELETE_WORD)
        self.next_word_btn = KeyboardButton(Commands.NEXT)
        self.main_menu_btn = KeyboardButton(Commands.MAIN_MENU)