import random
from enum import StrEnum


class Buttons(StrEnum):
    FINISH_BOT_CHAT = "Отключить бота💤"
    START_LEARNING = "Изучение английских слов...📖"
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово🚫"
    NEXT = "Дальше ⏭"
    MAIN_MENU = "Главное меню🔙"


class Commands(StrEnum):
    START = "start"
    EXIT = "exit"
    HELP = "help"

    @staticmethod
    def all_commands() -> list[str]:
        return [elem.value for elem in Commands]


class DictWord:
    """description of the word that is part of the dictionary."""

    def __init__(self, target_word: str, translate_word: str, *args) -> None:
        """Set the meaning of the target word and its variants.

        :param target_word: the meaning of the target word
        :param translate_word: translation of the target word
        :param args: additional erroneous translations of the target word
        """
        self.target_word = target_word
        self.translate_word = translate_word
        self.other_words = args
        self.correct_answers = 0
        self.wrong_answers = 0

    @property
    def translation_options(self) -> list:
        """Returns translation options."""
        word = [self.translate_word, *self.other_words]
        random.shuffle(word)
        return word

    @property
    def all_words(self) -> tuple:
        """Returns the target word and all its translation options.

        :return: returns a tuple of all words in a strictly specified order
        """
        return (
            self.target_word,
            self.translate_word,
            *self.other_words,
        )


class AddingWordToDictMixin:
    """Class describing the functionality of adding words to a dictionary.

    The class is not intended for independent use, but only adds additional
    features to the Dictionary class.
    """

    def __init__(self):
        """Set the target word and the meaning of its translation."""
        self.new_target_word = None
        self.new_translate_word = None

    def check_target_word(self, message):
        self.new_target_word = message.text.strip().upper()
        if self.bot_model.db.word_is_not_exist(self.new_target_word):
            self.bot_model.bot.send_message(
                message.chat.id,
                f"Введите перевод слова       {self.new_target_word}",
            )
            self.bot_model.another_action = self.check_translate_word
        else:
            self.add_new_word(message)

    def check_translate_word(self, message):
        self.new_translate_word = message.text.strip().upper()
        self.bot_model.bot.send_message(
            message.chat.id,
            "Введите через пробел три слова, с неправильным переводом...",
        )
        self.bot_model.another_action = self.check_other_words

    def check_other_words(self, message):
        words = message.text.strip().upper().split()
        if len(words) != 3:
            self.bot_model.bot.send_message(
                message.chat.id,
                "Я не разобрал введённых слов, повторите ввод пожалуйста!\n",
            )
            self.check_translate_word(message)
        else:
            dict_word = DictWord(
                self.new_target_word,
                self.new_translate_word,
                *words,
            )
            self.bot_model.db.add_word_to_db(dict_word.all_words)
            self.add_new_word(message, dict_word)

    def add_new_word(self, message, dict_word=None):
        self.bot_model.db.add_user_word_to_db(
            self.bot_model.user_id,
            self.new_target_word,
        )
        if dict_word is None:
            dict_word = self.bot_model.db.get_db_word(
                self.new_target_word,
            ).dict_word
        self.words.append(dict_word)
        count_words = len(self.words)
        self.bot_model.bot.send_message(
            message.chat.id,
            f"Слово {self.new_target_word} добавлено для изучения...😄\n"
            f"Теперь Вы изучаете {count_words} слов!",
        )
        self.curr_word = self.next_word
        self.show_curr_word(message)


class BaseWords:
    """The class describes the standard vocabulary of all users."""

    cat = ("KОШКА", "CAT", "CUT", "CENTER", "COTTON")
    dog = ("СОБАКА", "DOG", "DUCK", "DAGGER", "DUKE")
    hedgehog = ("ЁЖИК", "HEDGEHOG", "HEDGE", "HOG", "HEAD")
    green = ("ЗЕЛЁНЫЙ", "GREEN", "GIRL", "GARLIC", "FAR")
    red = ("КРАСНЫЙ", "RED", "RUDE", "ROD", "REED")
    money = ("ДЕНЬГИ", "MONEY", "MORE", "MONKEY", "MAKING")
    color = ("ЦВЕТ", "COLOR", "COULD", "COOL", "COLD")
    blue = ("ГОЛУБОЙ", "BLUE", "BLUFF", "BUFFER", "BEEF")
    elephant = ("СЛОН", "ELEPHANT", "ELEVEN", "LIVER", "CIRCUIT")
    rat = ("КРЫСА", "RAT", "RATE", "RUT", "ROUTE")
    squirrel = ("БЕЛКА", "SQUIRREL", "SQUIRE", "SQUARE", "SERVANT")
    wolf = ("ВОЛК", "WOLF", "LOFT", "WOULD", "WAFER")
    fox = ("ЛИСА", "FOX", "FAX", "FULL", "FEW")
    mountain = ("ГОРА", "MOUNTAIN", "MONTH", "MOURNING", "MUTUAL")
    fan = ("ВЕНТИЛЯТОР", "FAN", "FUN", "FONT", "FAINT")

    base_words = (
        cat,
        dog,
        hedgehog,
        green,
        red,
        money,
        color,
        blue,
        elephant,
        rat,
        squirrel,
        wolf,
        fox,
        mountain,
        fan,
    )

    @property
    def base_vocabulary(self) -> list[DictWord]:
        return [DictWord(*word) for word in BaseWords.base_words]
