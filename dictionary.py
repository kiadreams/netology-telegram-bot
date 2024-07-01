from data import Buttons, Word
from keyboards import DictionaryKeyboard
# from model import BotModel


class DictionaryMenu:

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.words = [
            Word("сумка", "bag", "backpack", "dog", "cat"),
            Word("собака", "dog", "gosh", "bog", "cat"),
            Word("кошка", "cat", "cut", "cot", "cattle"),
        ]
        self.base_dictionary_actions = {
            Buttons.NEXT: self.btn_show_next_word,
            Buttons.DELETE_WORD: self.btn_deleting_word_from_dict,
            Buttons.ADD_WORD: self.bnt_add_word_to_dict,
            Buttons.MAIN_MENU: self.model.btn_return_to_main_menu,
        }

    def btn_show_next_word(self, message): ...

    def bnt_add_word_to_dict(self, message): ...

    def btn_deleting_word_from_dict(self, message): ...


class Dictionary(DictionaryMenu):

    def __init__(self, model, user_id: int):
        super().__init__(model)
        self.user_id = user_id
        self.next_word_index = 0
        self.curr_word: Word | None = self.next_word

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

    def show_curr_word(self, message):
        print(self.curr_word.target_word)
        if self.curr_word is not None:
            kb = DictionaryKeyboard().add_words_to_kb(self.curr_word.words)
            self.model.bot.send_message(
                message.chat.id,
                f"Переведите слово: {self.curr_word.target_word}",
                reply_markup=kb,
            )
            self.model.actions = self.base_dictionary_actions
            self.model.add_actions(self.word_actions)
        else:
            self.model.bot.send_message(
                message.chat.id,
                "К сожалению в словаре нет слов для изучения...",
                reply_markup=DictionaryKeyboard().add_words_to_kb([]),
            )

    @property
    def word_actions(self) -> dict:
        if self.curr_word is not None:
            return {
                self.curr_word.translate_word: self.action_correct_answer,
                self.curr_word.other_words[0]: self.action_wrong_answer,
                self.curr_word.other_words[1]: self.action_wrong_answer,
                self.curr_word.other_words[2]: self.action_wrong_answer,
            }
        return {}

    def action_correct_answer(self, message):
        self.model.bot.send_message(
            message.chat.id,
            "Это правильный ответ, поехали дальше...",
        )
        self.curr_word.correct_answers += 1
        self.curr_word = self.next_word
        self.show_curr_word(message)
        # self.model.actions = self.base_dictionary_actions
        # self.model.add_actions(self.word_actions)

    def action_wrong_answer(self, message):
        self.model.bot.send_message(
            message.chat.id,
            "Это неправильный ответ... попробуем другое слово...",
        )
        self.curr_word.wrong_answers += 1
        self.curr_word = self.next_word
        self.show_curr_word(message)
        self.model.actions = self.base_dictionary_actions
        self.model.add_actions(self.word_actions)
