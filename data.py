import random
from enum import StrEnum


class Buttons(StrEnum):
    FINISH_BOT_CHAT = "Отключить бота"
    START_LEARNING = "Изучение английских слов..."
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово🔙"
    NEXT = "Дальше ⏭"
    MAIN_MENU = "Главное меню"

    @staticmethod
    def all_buttons() -> set[str]:
        return {elem.value for elem in Buttons}


class Commands(StrEnum):
    START = "start"
    EXIT = "exit"
    HELP = "help"

    @staticmethod
    def all_commands() -> list[str]:
        return [elem.value for elem in Commands]


class Word:

    def __init__(self, target_word: str, translate_word: str, *args) -> None:
        self.target_word = target_word
        self.translate_word = translate_word
        self.other_words = args
        self.correct_answers = 0
        self.wrong_answers = 0

    @property
    def words(self):
        word = [self.translate_word, *self.other_words]
        random.shuffle(word)
        return word


if __name__ == "__main__":
    print(Buttons.all_buttons())
    print()
    print(Commands.all_commands())
    print()
