import random
from model.data import ChangingDictMixin, BaseWords, Buttons
from view.keyboards import DictionaryKeyboard


class Dictionary(ChangingDictMixin):

    def __init__(self, model):
        """Set dictionary variables."""
        self.bot_model = model
        self.base_dictionary_actions = {
            Buttons.NEXT: self.btn_show_next_word,
            Buttons.DELETE_WORD: self.btn_deleting_word_from_dict,
            Buttons.MAIN_MENU: self.bot_model.btn_return_to_main_menu,
            Buttons.ADD_WORD: self.bnt_add_word_to_dict,
        }
        self.words = []
        self.curr_word: str | None = None
        super().__init__()

    def next_word(self) -> None:
        words = self.bot_model.db.get_words(self.bot_model.user_id)
        if words:
            self.curr_word = words[0][0]
            self.words = [elem[1] for elem in words]
        else:
            self.curr_word = None
            self.words = []


    @property
    def word_actions(self) -> dict:
        if self.curr_word is not None:
            correct_action = {self.words[0]: self.action_correct_answer}
            wrong_action = {
                word: self.action_wrong_answer for word in self.words[1:]
            }
            return {**correct_action, **wrong_action}
        return {}

    def show_curr_word(self, message):
        if self.curr_word is not None:
            words = self.words[:]
            random.shuffle(words)
            kb = DictionaryKeyboard().add_words_to_kb(words)
            self.bot_model.bot.send_message(
                message.chat.id,
                f"Переведите слово:    {self.curr_word}",
                reply_markup=kb,
            )
            self.bot_model.actions = {
                **self.base_dictionary_actions,
                **self.word_actions,
            }
        else:
            self.bot_model.bot.send_message(
                message.chat.id,
                "К сожалению в словаре нет слов для изучения...",
                reply_markup=DictionaryKeyboard().add_words_to_kb([]),
            )
            self.bot_model.actions = self.base_dictionary_actions

    def action_correct_answer(self, message):
        self.bot_model.bot.reply_to(
            message,
            "🎉, Это правильный ответ!!!,\nПоехали дальше...",
        )
        self.bot_model.db.update_user_word(
            self.bot_model.user_id,
            self.curr_word,
            corr_answers=1,
        )
        self.next_word()
        self.show_curr_word(message)

    def action_wrong_answer(self, message):
        self.bot_model.bot.reply_to(
            message,
            "НЕПРАВИЛЬНО... 🤦‍♂️\nДавайте попробуем ещё раз...❗",
        )
        self.bot_model.db.update_user_word(
            self.bot_model.user_id,
            self.curr_word,
            wrong_answers=1,
        )
        self.show_curr_word(message)

    def btn_show_next_word(self, message):
        self.next_word()
        self.show_curr_word(message)

    def bnt_add_word_to_dict(self, message):
        self.bot_model.bot.send_message(
            message.chat.id,
            "Введите 🇷🇺 слово, которое хотите добавить... ",
            reply_markup=DictionaryKeyboard.delete_keyboard(),
        )
        self.bot_model.actions = {}
        self.bot_model.another_action = self.check_target_word

    def btn_deleting_word_from_dict(self, message) -> None:
        self.bot_model.bot.send_message(
            message.chat.id,
            "Введите слово, которое хотите удалить... ",
            reply_markup=DictionaryKeyboard.delete_keyboard(),
        )
        self.bot_model.actions = {}
        self.bot_model.another_action = self.delete_word_from_db

    def download_user_words(self, user_id: int, name: str, last_name: str):
        if self.bot_model.db.words_table_is_empty():
            for words in BaseWords().base_vocabulary:
                self.bot_model.db.add_word_to_db(*words)
        if self.bot_model.db.user_is_not_exist(user_id):
            self.bot_model.db.add_user_to_db(user_id, name, last_name)
            for words in BaseWords().base_vocabulary:
                self.bot_model.db.add_user_word_to_db(user_id, words[0])
        self.next_word()
