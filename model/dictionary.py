from model.data import Buttons, DictWord
from view.keyboards import DictionaryKeyboard

from model.bot_model import BotModel

from database.db_model import UserWord


class DictionaryMenu:

    def __init__(self, model):
        super().__init__()
        self.bot_model = model
        self.base_dictionary_actions = {
            Buttons.NEXT: self.btn_show_next_word,
            Buttons.DELETE_WORD: self.btn_deleting_word_from_dict,
            Buttons.ADD_WORD: self.bnt_add_word_to_dict,
            Buttons.MAIN_MENU: self.bot_model.btn_return_to_main_menu,
        }

    def btn_show_next_word(self, message): ...

    def bnt_add_word_to_dict(self, message): ...

    def btn_deleting_word_from_dict(self, message): ...


class DictionaryAddWordMenu:
    pass


class Dictionary(DictionaryMenu):

    def __init__(self, model: BotModel, user_id: int):
        super().__init__(model)
        self.user_id = user_id
        self.words: list[DictWord] | None = None
        self.next_word_index = 0
        self.curr_word: DictWord | None = None

    @property
    def next_word(self) -> DictWord | None:
        if self.words:
            word = self.words[self.next_word_index]
            if self.next_word_index + 2 > len(self.words):
                self.next_word_index = 0
            else:
                self.next_word_index += 1
            return word
        return None

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

    def show_curr_word(self, message):
        if self.curr_word is not None:
            kb = DictionaryKeyboard().add_words_to_kb(self.curr_word.all_words)
            self.bot_model.bot.send_message(
                message.chat.id,
                f"Переведите слово:       {self.curr_word.target_word}",
                reply_markup=kb,
            )
            self.bot_model.actions = self.base_dictionary_actions
            self.bot_model.add_actions(self.word_actions)
        else:
            self.bot_model.bot.send_message(
                message.chat.id,
                "К сожалению в словаре нет слов для изучения...",
                reply_markup=DictionaryKeyboard().add_words_to_kb([]),
            )

    def action_correct_answer(self, message):
        self.bot_model.bot.send_message(
            message.chat.id,
            "🎉, Это правильный ответ!!!,\nПоехали дальше...",
        )
        self.curr_word.correct_answers += 1
        self.bot_model.db.update_user_word(self.user_id, self.curr_word)
        self.curr_word = self.next_word
        self.show_curr_word(message)

    def action_wrong_answer(self, message):
        self.bot_model.bot.send_message(
            message.chat.id,
            "НЕПРАВИЛЬНО... 🤦‍♂️\n"
            f"Правильный перевод       {self.curr_word.translate_word}\n"
            "Попробуем другое слово...",
        )
        self.curr_word.wrong_answers += 1
        self.bot_model.db.update_user_word(self.user_id, self.curr_word)
        self.curr_word = self.next_word
        self.show_curr_word(message)

    def btn_show_next_word(self, message):
        self.curr_word = self.next_word
        self.show_curr_word(message)

    def bnt_add_word_to_dict(self, message):
        self.bot_model.bot.send_message(
            message.chat.id,
            "Введите нужное слово... ",
            reply_markup=DictionaryKeyboard.delete_keyboard(),
        )
        self.bot_model.another_action = self.check_target_words

    def check_target_words(self, message):
        word = message.text.strip().upper()
        print(word)
        if self.bot_model.db.word_is_exist(word):
            pass
        else:
            pass
        self.bot_model.bot.send_message(
            message.chat.id,
            f"Введенные слова добавлены {word}",
        )
        self.show_curr_word(message)

    def btn_deleting_word_from_dict(self, message):
        if self.words:
            self.bot_model.db.delete_word(
                self.bot_model.user_id,
                self.curr_word.target_word,
            )
            self.words.remove(self.curr_word)
            self.next_word_index -= 1
            self.curr_word = self.next_word
            self.show_curr_word(message)
        else:
            self.bot_model.bot.send_message(
                message.chat.id,
                "Словарь и так пуст, сначала добавьте в него слова... 🤦‍♂️",
                reply_markup=DictionaryKeyboard().add_words_to_kb([]),
            )

    def load_words_from_db(self, user_id):
        self.words = self.bot_model.db.get_all_user_words(user_id)
        self.curr_word = self.next_word
