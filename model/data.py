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


class ChangingDictMixin:
    """Class describing the functionality of adding words to a dictionary.

    The class is not intended for independent use, but only adds additional
    features to the Dictionary class.
    """

    def __init__(self):
        """Set the target word and the meaning of its translation."""
        self.new_word = None

    def check_target_word(self, message):
        self.new_word = message.text.strip().upper()
        if self.bot_model.db.word_is_not_exist(self.new_word):
            self.bot_model.bot.send_message(
                message.chat.id,
                f"Введите перевод слова       {self.new_word}\n"
                "на английский язык 🇺🇸!",
            )
            self.bot_model.another_action = self.check_translate_word
        else:
            self.add_new_word(message)

    def check_translate_word(self, message):
        translate_word = message.text.strip().upper()
        self.bot_model.db.add_word_to_db(self.new_word, translate_word)
        self.add_new_word(message)

    def add_new_word(self, message):
        self.bot_model.db.add_user_word_to_db(
            self.bot_model.user_id,
            self.new_word,
        )
        num_words = self.bot_model.db.get_num_of_user_words(
            self.bot_model.user_id,
        )
        self.bot_model.bot.send_message(
            message.chat.id,
            f"Слово {self.new_word} добавлено для изучения...😄\n"
            f"Теперь Вы изучаете {num_words} слов!",
        )
        self.next_word()
        self.show_curr_word(message)

    def delete_word_from_db(self, message) -> None:
        word = message.text.strip().upper()
        if self.bot_model.db.user_word_is_not_exist(
            self.bot_model.user_id,
            word,
        ):
            self.bot_model.bot.send_message(
                message.chat.id,
                f"Указанное слово {word} Вы не изучаете...🤷‍♂️"
            )
        else:
            self.bot_model.db.delete_word(self.bot_model.user_id, word)
            num_words = self.bot_model.db.get_num_of_user_words(
                self.bot_model.user_id,
            )
            self.bot_model.bot.send_message(
                message.chat.id,
                f"Слово {word} удалено из Вашего словаря...👌\n"
                f"Теперь Вы изучаете {num_words} слов! ️",
            )
            self.next_word()
        self.show_curr_word(message)


class BaseWords:
    """The class describes the standard vocabulary of all users."""

    cat = ("КОШКА", "CAT", "CUT", "CENTER", "COTTON")
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
    def base_vocabulary(self) -> list[tuple]:
        return [word[:2] for word in BaseWords.base_words]
