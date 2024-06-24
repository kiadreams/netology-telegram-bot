import re
import traceback
from random import randrange
from typing import Any
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from db import ModelDb, Users, Photos, Clients
from vk_data import KeyWord, Meths, DftSrcCriteria
from additional_data import perform_authorization


class Photo:

    def __init__(self, data: dict):
        self.album_id = data.get('album_id', 0)
        self.date = data.get('date', 0)
        self.owner_id = data.get('owner_id', 0)
        self.photo_id = data.get('id', 0)
        self.photo_sizes = data.get('sizes', [])
        self.photo_link = data.get('sizes', [{}])[-1].get('url', '')
        self.count_likes = data.get('likes', {}).get('count', 0)
        self.user_likes = data.get('likes', {}).get('user_likes', 0)
        self.web_view_token = data.get('web_view_token', '')
        self.user_mark = False

    def get_photo_record_for_db(self) -> Photos:
        db_photo = Photos(photo_id=self.photo_id, owner_id=self.owner_id,
                          photo_link=self.photo_link, user_mark=self.user_mark)
        return db_photo

    def init_photo_from_db_record(self, ph: Photos) -> None:
        if ph is not None:
            self.photo_id = ph.photo_id
            self.owner_id = ph.owner_id
            self.photo_link = ph.photo_link
            self.user_mark = ph.user_mark


class User:
    """Класс, описывающий пользователя социальной сети Вконтакте.

    Класс на вход принимает один параметр - item, находящийяся, в ответе на
    запрос 'users.search', в поле 'items'.
    :param data: является словарeм, описывающим поля пользователя
    """

    def __init__(self, data: dict):
        self.id: int = data.get('id', 0)
        self.first_name: str = data.get('first_name', '')
        self.last_name: str = data.get('last_name', '')
        self.bdate: str = data.get('bdate', '')
        self.city_id: int = data.get('city', {}).get('id', 0)
        self.city_title: str = data.get('city', {}).get('title', '')
        self.sex: int = data.get('sex', 0)
        self.prf_link = f'https://vk.com/id{self.id}'
        self.list_photos: list[Photo] = []

    def update_user_data(self, data: dict) -> None:
        """Обновляет информацию о пользователе"""
        self.id: int = data.get('id', 0)
        self.first_name: str = data.get('first_name', '')
        self.last_name: str = data.get('last_name', '')
        self.bdate: str = data.get('bdate', '')
        self.city_id: int = data.get('city', {}).get('id', 0)
        self.city_title: str = data.get('city', {}).get('id', '')
        self.sex: int = data.get('sex', 0)

    def get_age(self) -> int:
        if self.bdate:
            day, month, year = map(int, self.bdate.split('.'))
            birthday = datetime(year, month, day)
            cur_day = datetime.now()
            y, m, d = birthday.year, cur_day.month, cur_day.day
            return cur_day.year - y - (birthday > datetime(y, m, d))
        else:
            return 0

    def get_user_record_for_db(self) -> Users:
        db_user = Users(user_id=self.id, first_name=self.first_name,
                        last_name=self.last_name, prf_link=self.prf_link)
        return db_user

    def init_user_from_db_record(self, user: Users) -> None:
        self.id = user.user_id
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.prf_link = user.prf_link

    def get_user_info(self) -> str:
        text = (
            f'''
            {self.last_name} {self.first_name}
            {self.prf_link}
            '''
        )
        return text

    def get_user_photos(self, count=3, popular=True) -> list[Photo]:
        self.list_photos.sort(key=lambda photo: photo.count_likes,
                              reverse=popular)
        return self.list_photos[:count]

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class UserVkApi(VkApi):

    def __init__(self, token: str = None, user_id: int = None) -> None:
        super().__init__(token=token, api_version='5.191')
        self.admin = User({'id': user_id})
        self._uploading_client_data()

    def _uploading_client_data(self) -> None:
        """Загружеет данные пользователя-клиента.

        Проверяет наличие и актуальност токена и id пользователя с помощью
        запроса на получение его данных, при неуспешной загрузке данных,
        выполняет авторизацию пользователя с последующей повторной попыткой
        загрузки данных клиента.
        :exception WebDriverException
        :exception ApiError
        :return:
        """
        if client_data := self.get_users_info([self.admin.id]):
            self.admin.update_user_data(client_data[0])
        else:
            token, user_id = perform_authorization(self.app_id)
            print(f'Ваш новый токен: {token}')
            self.token = {'access_token': token}
            self.admin.id = user_id
            if client_data := self.get_users_info([self.admin.id]):
                self.admin.update_user_data(client_data[0])

    def get_users_info(self, user_ids: list[int] = None) -> list[dict]:
        """Метод возвращает данные пользователя по его id.
        :exception ApiError:
        :return:
        """
        if user_ids is not None:
            user_ids = ','.join(map(str, user_ids))
        params = {
            'user_ids': user_ids,
            'fields': 'city,bdate,sex,interests'
        }
        try:
            if response := self.method(Meths.USERS_GET, params):
                return response
            else:
                return []
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить данные пользователей...')
            return []

    def search_users(self, params: dict) -> list[dict]:
        try:
            return self.method(Meths.USER_SEARCH, params).get('items', [])
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить список пользователей...')
            return []

    def get_user_photos(self, user_id: int) -> list[dict]:
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': '1'}
        try:
            return self.method(Meths.PHOTOS_GET, params).get('items', [])
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить список фото пользователей...')
            return []

    def get_city(self, city_name: str, count=1) -> list[dict]:
        params = {'q': city_name, 'need_all': 0, 'count': count}
        try:
            return self.method(Meths.GET_CITY, params).get('items', [])
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить города...')
            return []


class GroupVkApi(VkApi):

    def __init__(self, group_token: str) -> None:
        super().__init__(token=group_token, api_version='5.191')
        self.id_list_of_people = {}

    def show_kb(self, user_id: int, message: str, kb='') -> bool:
        if self._send_msg(user_id, message, kb):
            return True
        else:
            print('Не получилось отообразить клавиатуру...')
            return False

    def hide_kb(self, user_id: int, message: str, kb='') -> bool:
        if self._send_msg(user_id, message, kb):
            return True
        else:
            print('Не получилось отключить клавиатуру...')
            return False

    def write_msg(self, user_id: int, message: str) -> bool:
        return self._send_msg(user_id, message)

    def send_attachment(self, user_id: int, message, attachment, r_id=True):
        random_id = randrange(10 ** 7) if r_id else 0
        values = {'user_id': user_id,
                  'random_id': random_id,
                  'message': message,
                  'attachment': attachment}
        try:
            self.method(Meths.MESSAGES_SEND, values)
            return True
        except ApiError:
            traceback.print_exc()
            print('Не получилось отпарвить фото...')
            return False

    def _send_msg(self, user_id: int, message='', kb='', r_id=True) -> bool:
        random_id = randrange(10 ** 7) if r_id else 0
        values = {'user_id': user_id,
                  'message': message,
                  'random_id': random_id,
                  'keyboard': kb}
        try:
            self.method(Meths.MESSAGES_SEND, values)
            return True
        except ApiError:
            traceback.print_exc()
            print('Не получилось отпарвить сообщение...')
            return False


class Criteria:
    STR_SEX = {0: 'не важен', 1: 'женский', 2: 'мужской'}

    def __init__(self):
        self.age_from = DftSrcCriteria.MIN_AGE
        self.age_to = DftSrcCriteria.MAX_AGE
        self.sex = 0
        self.city_id = 0
        self.city_title = ''
        self.is_criteria_changed = False
        self.offset = 0

    def check_user(self, user: User) -> bool:
        return (self.check_sex(user.sex)
                and self.check_user_age(user.get_age())
                and self.check_user_city(user.city_id))

    def check_user_age(self, age: int) -> bool:
        return self.age_from <= age <= self.age_to

    def check_user_city(self, city_id: int) -> bool:
        return city_id == self.city_id

    def check_sex(self, sex: int) -> bool:
        return True if not self.sex else sex == self.sex

    def set_criteria_from_user(self, user: User) -> None:
        self.age_from = user.get_age()
        self.age_to = user.get_age()
        self.sex = user.sex if user.sex else 0
        self.city_id = user.city_id
        self.city_title = user.city_title

    def get_descr_criteria(self) -> str:
        str_sex = self.STR_SEX.get(self.sex, 'неважен')
        text = (
            f'''
            Критерии поиска:
            - возраст: от {self.age_from} до {self.age_to} лет;
            - пол: {str_sex};
            - город: {self.city_title}.
            '''
        )
        return text

    def get_search_params(self, count: int) -> dict:
        search_params = {'sex': self.sex,
                         'city_id': self.city_id,
                         'age_from': self.age_from,
                         'age_to': self.age_to,
                         'has_photo': 1,
                         'fields': 'city,sex,bdate',
                         'count': count,
                         'offset': self.offset}
        return search_params


class SearchEngine(Criteria):

    def __init__(self, api: UserVkApi):
        super().__init__()
        self.api = api
        self.is_search_going_on = False
        self.blacklist_ids = set()
        self.user_list = []

    def get_data_users(self) -> bool:
        params = self.get_search_params(count=DftSrcCriteria.STEP_SEARCH)
        if users_data := self.api.search_users(params):
            self.offset += DftSrcCriteria.STEP_SEARCH
            for data in users_data:
                if not data.get('is_closed', 1):
                    user = User(data)
                    if (user.id not in self.blacklist_ids
                            and self.check_user(user)):
                        user.list_photos = self.upload_photos(user.id)
                        self.user_list.append(user)
            return True
        else:
            return False

    def upload_photos(self, user_id: int) -> list[Photo]:
        if user_photos := self.api.get_user_photos(user_id):
            photos = []
            for data in user_photos:
                photo = Photo(data)
                photos.append(photo)
            return photos
        else:
            return []

    def start_found_users(self) -> User | None:
        self.is_search_going_on = True
        return self.get_next_user()

    def stop_found_users(self):
        self.is_search_going_on = False
        self.offset = 0
        self.user_list.clear()

    def get_next_user(self) -> User | None:
        if self.user_list:
            return self.user_list.pop(0)
        else:
            self.get_data_users()
            try:
                return self.user_list.pop(0)
            except IndexError:
                print('Всё!!! Больше никого не нашёл...')
                return None

    def search_city(self, city_name: str, count=1) -> list[dict]:
        return self.api.get_city(city_name, count)


class ActionInterface:

    def __init__(self):
        self.curr_action = {}
        self.curr_kb = None

    def _get_start_dialog_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.FND_PEOPLE, VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.STOP_USER_BOT, VkKeyboardColor.NEGATIVE)

        key_word = {KeyWord.FND_PEOPLE: self._go_choose_view_options,
                    KeyWord.STOP_USER_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_choosing_actions_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.FND_NEW_PEOPLE,
                            VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.SHOW_BLACKLIST,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.SHOW_FAVORITES,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.CLEAR_BLACKLIST, VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.CLEAR_HISTORY, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.STOP_USER_BOT, VkKeyboardColor.NEGATIVE)

        key_word = {KeyWord.FND_NEW_PEOPLE: self._go_search_people,
                    KeyWord.SHOW_BLACKLIST: self._go_blacklist_view,
                    KeyWord.SHOW_FAVORITES: self._go_favorites_view,
                    KeyWord.CLEAR_HISTORY: self._clear_history,
                    KeyWord.CLEAR_BLACKLIST: self._clear_blacklist,
                    KeyWord.STOP_USER_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_criteria_selection_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.LETS_SHOW, VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.CHOOSE_CITY, VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.CHOOSE_AGE, VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.CHOOSE_SEX, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.COME_BACK, VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyWord.STOP_USER_BOT, VkKeyboardColor.NEGATIVE)

        key_word = {KeyWord.COME_BACK: self._go_come_back,
                    KeyWord.CHOOSE_CITY: self._choose_city,
                    KeyWord.CHOOSE_AGE: self._choose_age,
                    KeyWord.CHOOSE_SEX: self._choose_sex,
                    KeyWord.LETS_SHOW: self._go_browsing,
                    KeyWord.STOP_USER_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_queue_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.IS_NOT_INTERESTING,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.IS_INTERESTING,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.NEXT_USER, VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.COME_BACK, VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyWord.STOP_USER_BOT, VkKeyboardColor.NEGATIVE)

        key_word = {KeyWord.IS_NOT_INTERESTING: self._add_to_blacklist,
                    KeyWord.IS_INTERESTING: self._add_to_favorites,
                    KeyWord.NEXT_USER: self._show_next_user,
                    KeyWord.COME_BACK: self._go_come_back,
                    KeyWord.STOP_USER_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_viewing_history_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.PREVIOUS_PERSON, VkKeyboardColor.PRIMARY)
        keyboard.add_button(KeyWord.DELETE_FROM_LIST, VkKeyboardColor.NEGATIVE)
        keyboard.add_button(KeyWord.NEXT_PERSON, VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.COME_BACK, VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(KeyWord.STOP_USER_BOT, VkKeyboardColor.NEGATIVE)

        key_word = {KeyWord.NEXT_PERSON: self._show_next_person,
                    KeyWord.DELETE_FROM_LIST: self._delete_user,
                    KeyWord.PREVIOUS_PERSON: self._show_previous_person,
                    KeyWord.COME_BACK: self._go_come_back,
                    KeyWord.STOP_USER_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    # Реализация комыды "exit" и кнопки "хватит", общих для всего интерфейса
    def exit_from_vkbot(self, message=''):
        pass

    def stop_bot_dialog(self, message=''):
        pass

    # Реализация интерфейса стартовой клавиатуры
    def start_bot_dialog(self, message=''):
        pass

    def _go_choose_view_options(self, message=''):
        pass

    # Реализация клавиатуры выбора вариантов просмотра пользователей
    def _go_search_people(self, message=''):
        pass

    def _go_blacklist_view(self, message=''):
        pass

    def _go_favorites_view(self, message=''):
        pass

    def _clear_history(self, message=''):
        pass

    def _clear_blacklist(self, message=''):
        pass

    # Реализация клавиатуры выбора опций поиска новых лидей
    def _choose_city(self, message=''):
        pass

    def _choose_age(self, message=''):
        pass

    def _choose_sex(self, message=''):
        pass

    def _go_browsing(self, message=''):
        pass

    def _show_next_user(self):
        pass

    # Реализация клавивтуры просмотра новых пользователей
    def _add_to_blacklist(self, message=''):
        pass

    def _add_to_favorites(self, message=''):
        pass

    def _show_previous_person(self, message=''):
        pass

    def _delete_user(self, message=''):
        pass

    def _show_next_person(self, message=''):
        pass

    # Реализация кнопки "назад" и "следующий" общей для нескольких клавиатур
    def _go_come_back(self, message=''):
        pass


class UserBot(ActionInterface):
    AGE_PATTERN = re.compile(r'\d{1,3}')

    def __init__(self, user_api: UserVkApi, user: User,
                 bot_api: GroupVkApi, model_db: ModelDb) -> None:
        super().__init__()
        self.s_engin = SearchEngine(user_api)
        self.db = model_db
        self.api = bot_api
        self.client = user
        self.curr_user: User | None = None
        self.blacklist = set()
        self.favorite_list = set()
        self.viewing_list: list | None = None
        self.marker = 0
        self.max_marker = 0
        self.another_action: Any = None

    def event_handling(self, event: Event) -> None:
        action = self.curr_action.get(event.text)
        if action is not None:
            action()
        else:
            self.another_action(event)

    def start_bot_dialog(self, msg='') -> None:
        self.curr_kb, self.curr_action = self._get_start_dialog_kb()
        self.another_action = self.do_another_action
        bl_users = self.db.download_users(self.client.id, blacklisted=True)
        self.blacklist = self.cnvrt_db_rec_to_users(bl_users)
        fl_users = self.db.download_users(self.client.id, blacklisted=False)
        self.favorite_list = self.cnvrt_db_rec_to_users(fl_users)
        self.s_engin.blacklist_ids = {usr.id for usr in self.blacklist}
        self.s_engin.set_criteria_from_user(self.client)
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def stop_bot_dialog(self, msg='Ладно, и мне пора... :-)') -> None:
        self.api.hide_kb(self.client.id, msg,
                         self.curr_kb.get_empty_keyboard())

    def _go_choose_view_options(self, msg='Где будем просматривать?') -> None:
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def _go_blacklist_view(self, msg='Посмотрим...') -> None:
        if self.set_viewing_options(self.blacklist, msg):
            self.show_user_info(self.viewing_list[self.marker])
        else:
            self.api.write_msg(self.client.id, 'Список пуст...')

    def _go_favorites_view(self, msg='Посмотрим...') -> None:
        if self.set_viewing_options(self.favorite_list, msg):
            self.show_user_info(self.viewing_list[self.marker])
        else:
            self.api.write_msg(self.client.id, 'Список пуст...')

    def _go_search_people(self, msg='') -> None:
        self.curr_kb, self.curr_action = self._get_criteria_selection_kb()
        msg = '\n'.join([self.s_engin.get_descr_criteria(),
                         'Но можете изменить эти данные...'])
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())
        self.another_action = self.do_another_action
        # self.api.write_msg(self.client.id, msg)

    def _clear_history(self, msg='Пока реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _clear_blacklist(self, msg='Пока реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _go_come_back(self, msg='Передумали... :-(') -> None:
        if self.s_engin.is_search_going_on:
            self.curr_user = None
            self.s_engin.stop_found_users()
            self.s_engin.set_criteria_from_user(self.client)
        elif self.viewing_list is not None:
            self.marker = 0
            self.max_marker = 0
            self.viewing_list = None
        elif self.s_engin.is_criteria_changed:
            self.s_engin.set_criteria_from_user(self.client)
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def _choose_city(self, msg='') -> None:
        msg = 'Напишите название города, в котором будем искать людей...'
        if self.api.hide_kb(self.client.id, msg,
                            self.curr_kb.get_empty_keyboard()):
            self.curr_action = {KeyWord.STOP_USER_BOT: self.stop_bot_dialog,
                                KeyWord.COME_BACK: self._go_come_back}
            self.another_action = self._checking_city

    def _choose_age(self, msg='') -> None:
        msg = 'Укажите от какого и до какого возраста Вас интересуют люди...'
        self.api.hide_kb(self.client.id, msg,
                         self.curr_kb.get_empty_keyboard())
        self.curr_action = {KeyWord.STOP_USER_BOT: self.stop_bot_dialog,
                            KeyWord.COME_BACK: self._go_come_back}
        self.another_action = self._checking_age_input

    def _choose_sex(self, msg='') -> None:
        msg = ('Укажите, кто вас интересует:\n'
               '\t"0" - не имеет значения;\n'
               '\t"1" - люди женского пола;\n'
               '\t"2" - люди мужского пола.')
        self.api.hide_kb(self.client.id, msg,
                         self.curr_kb.get_empty_keyboard())
        self.curr_action = {KeyWord.STOP_USER_BOT: self.stop_bot_dialog,
                            KeyWord.COME_BACK: self._go_come_back}
        self.another_action = self._checking_sex_input

    def _checking_city(self, event: Event):
        if city := self.s_engin.search_city(event.text, 1):
            self.s_engin.city_id = city[0].get('id', self.client.city_id)
            self.s_engin.city_title = city[0].get('title',
                                                  self.client.city_title)
            self.s_engin.is_criteria_changed = True
            self._go_search_people()
        else:
            self.api.write_msg(self.client.id,
                               'Такой город я не знаю: введите'
                               ' другое название!\nИли, если передумали - '
                               'то наберите "назад", чтобы вернуться или '
                               '"хватит", чтобы закончить нашу беседу...')

    def _checking_age_input(self, event: Event) -> None:
        if all_ages := self.AGE_PATTERN.findall(event.text):
            try:
                all_ages = list(
                    filter(lambda age: 0 < age < 120, map(int, all_ages))
                )
                self.s_engin.age_from = min(all_ages)
                self.s_engin.age_to = max(all_ages)

            except ValueError:
                self.api.write_msg(
                    self.client.id,
                    'Что-то я не понял какой возраст мне искать...')
            else:
                self.s_engin.is_criteria_changed = True
                self._go_search_people()
        else:
            self.api.write_msg(self.client.id,
                               'Вы не указали ни одного возраста...')
            self.api.write_msg(
                self.client.id,
                'Если передумали - наберите "назад", чтобы вернуться'
                ' или "хватит", чтобы прервать диалог...')

    def _checking_sex_input(self, event: Event) -> None:
        try:
            sex = int(event.text)
        except ValueError:
            self.api.write_msg(self.client.id,
                               'Введите пожалуйста только одну цифру: "0" или'
                               ' "1" или "2"!\nЕсли передумали - наберите '
                               '"назад", чтобы вернуться или "хватит", чтобы'
                               ' прервать диалог...')
        else:
            if sex not in [0, 1, 2]:
                self.api.write_msg(self.client.id,
                                   'цифра введена неправильная...'
                                   ' попробуйте ещё раз...\nЕсли передумали - '
                                   'наберите "назад", чтобы вернуться или'
                                   ' "хватит", чтобы прервать диалог...')
            else:
                self.s_engin.sex = sex
                self.s_engin.is_criteria_changed = True
                self._go_search_people()

    def _go_browsing(self, msg='Поищем...') -> None:
        self.curr_kb, self.curr_action = self._get_queue_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())
        self.curr_user = self.s_engin.start_found_users()
        self.show_user_info(self.curr_user)

    def _show_next_user(self) -> None:
        self.curr_user = self.s_engin.get_next_user()
        self.show_user_info(self.curr_user)

    def _add_to_blacklist(self, msg='Занес в черный список...:-(') -> None:
        if self.curr_user in self.favorite_list:
            message = 'Данный пользователь занесен в избранное...'
            self.api.write_msg(self.client.id, message)
        elif self.curr_user in self.blacklist:
            message = 'Данный пользователь уже занесен в чёрный список...'
            self.api.write_msg(self.client.id, message)
        else:
            args = self.cnvrt_users_to_db_rec(self.curr_user, self.client.id)
            try:
                self.db.write_users_to_db(*args, blacklisted=True)
            except IntegrityError:
                print('не получилось добавить пользователя в список...')
            else:
                self.blacklist.add(self.curr_user)
                self.s_engin.blacklist_ids.add(self.curr_user.id)
                self.api.write_msg(self.client.id, msg)

    def _add_to_favorites(self, msg='Добавил к избранным...:-)') -> None:
        if self.curr_user in self.favorite_list:
            message = 'Данный пользователь уже занесен в избранное...'
            self.api.write_msg(self.client.id, message)
        elif self.curr_user in self.blacklist:
            message = 'Данный пользователь занесен в чёрный список...'
            self.api.write_msg(self.client.id, message)
        else:
            args = self.cnvrt_users_to_db_rec(self.curr_user, self.client.id)
            try:
                self.db.write_users_to_db(*args, blacklisted=False)
            except IntegrityError:
                print('не получилось добавить пользователя в список...')
            else:
                self.favorite_list.add(self.curr_user)
                self.api.write_msg(self.client.id, msg)

    def _show_previous_person(self, msg='Список пуст...') -> None:
        if self.viewing_list:
            self.marker -= 1
            if abs(self.marker) > self.max_marker:
                self.marker = 0
            self.show_user_info(self.viewing_list[self.marker])
        else:
            self.api.write_msg(self.client.id, msg)

    def _delete_user(self, msg='Пока не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _show_next_person(self, msg='Список пуст...') -> None:
        if self.viewing_list:
            self.marker += 1
            if abs(self.marker) > self.max_marker:
                self.marker = 0
            self.show_user_info(self.viewing_list[self.marker])
        else:
            self.api.write_msg(self.client.id, msg)

    def do_another_action(self, event: Event) -> None:
        msg = '-'.join([event.text, 'я не понимаю, чего Вы от меня хотите...'])
        self.api.write_msg(self.client.id, msg)

    def show_user_info(self, user: User) -> None:
        if user is not None:
            msg = user.get_user_info()
            attachments = []
            for pht in user.get_user_photos():
                attachment = f'photo{pht.owner_id}_{pht.photo_id}'
                attachments.append(attachment)
            self.api.send_attachment(self.client.id, msg,
                                     ','.join(attachments))
        else:
            self.api.write_msg(self.client.id, 'Нет пользователей...')
            self._go_come_back('Может изменим варианты просмотра...')

    def set_viewing_options(self, special_list: set, message: str) -> bool:
        if special_list:
            self.marker = 0
            self.max_marker = len(special_list) - 1
            self.viewing_list = list(special_list)
            self.curr_kb, self.curr_action = self._get_viewing_history_kb()
            self.api.show_kb(self.client.id, message,
                             self.curr_kb.get_keyboard())
            return True
        else:
            return False

    @staticmethod
    def cnvrt_users_to_db_rec(user: User, client_id: int) -> tuple:
        """Метод возвращает подготовленные записи в БД

        Порядок возврата результата важен для передачи в метод модели БД для
        последующей записей этих данных
        :param user:
        :param client_id:
        :return: tuple[Users, int, list[Photos]
        """
        db_user = user.get_user_record_for_db()
        db_client = Clients(client_id=client_id)
        db_photos = [ph.get_photo_record_for_db() for ph in user.list_photos]
        return db_user, db_client, db_photos

    @staticmethod
    def cnvrt_db_rec_to_users(db_users: dict) -> set[User]:
        users = set()
        for db_u, db_phs in db_users.items():
            user = User({})
            user.init_user_from_db_record(db_u)
            user_phs: list = []
            for db_ph in db_phs:
                if db_ph is not None:
                    ph = Photo({})
                    ph.init_photo_from_db_record(db_ph)
                    user_phs.append(ph)
            user.list_photos.extend(user_phs)
            users.add(user)
        return users
