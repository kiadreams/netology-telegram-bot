import random

from model import BotModel

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


class Dictionary:

    def __init__(self, model: BotModel, user_id):
        self.model = model
        self.user_id = user_id
        self.next_word_index = 0
        self.words = [
            Word("сумка", "bag", "backpack", "dog", "cat"),
            Word("собака", "dog", "gosh", "bog", "cat"),
            Word("кошка", "cat", "cut", "cot", "cattle"),
        ]
        self.curr_word = self.next_word

    @property
    def next_word(self) -> Word | None:
        if self.words:
            word = self.words[self.next_word_index]
            if self.next_word_index + 2 > len(self.words):
                self.next_word_index = 0
            else:
                self.next_word_index += 1
            return word
        return None

    @property
    def word_actions(self):
        return {
            self.curr_word.target_word: self.action_correct_answer,
            self.curr_word.other_words[0]: self.action_wrong_answer,
            self.curr_word.other_words[1]: self.action_wrong_answer,
            self.curr_word.other_words[2]: self.action_wrong_answer,
        }

    def show_curr_word(self, message):
        self.model.bot.send_message(
            message.chat.id,
            f"Укажите перевод слова: {self.curr_word.target_word}",
            reply_markup=keyboards.WordsKeyboard(self.curr_word.words).keyboard,
        )

    def action_correct_answer(self, message):
        self.model.bot.send_message(
            message.chat.id,
            "Это правильный ответ, пошли дальше..."
        )
        self.curr_word.correct_answers += 1
        self.curr_word = self.next_word
        self.model.actions = self.model.english_word_menu_actions
        self.model.add_actions()

    def action_wrong_answer(self, message):
        pass

    def btn_start_english_learning(self, message):
        self.dictionary.nex_word_index = 0
        word = self.dictionary.curr_word
        self.bot.send_message(
            message.chat.id,
            f"Укажите перевод слова: {word.target_word}",
            reply_markup=keyboards.WordsKeyboard(word.words).keyboard,
        )
        self.actions = self.english_word_menu_actions
        self.add_actions(self.dictionary.word_actions)


if __name__ == "__main__":
    my_dict = Dictionary(45)
    print(my_dict.curr_word.words)
    print(my_dict.curr_word.words)
    print(my_dict.curr_word.words)
