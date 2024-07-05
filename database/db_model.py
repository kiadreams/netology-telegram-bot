from typing import Any

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from model.data import DictWord


Base = declarative_base()


class Word(Base):
    __tablename__ = "words"

    target_word = sq.Column(sq.String(length=50), primary_key=True)
    translate_word = sq.Column(sq.String(length=50), nullable=False)
    eng_word1 = sq.Column(sq.String(length=50), nullable=False)
    eng_word2 = sq.Column(sq.String(length=50), nullable=False)
    eng_word3 = sq.Column(sq.String(length=50), nullable=False)

    @property
    def dict_word(self):
        return DictWord(
            self.target_word,
            self.translate_word,
            self.eng_word1,
            self.eng_word2,
            self.eng_word3,
        )


class User(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=50), nullable=False)
    last_name = sq.Column(sq.String(length=50), nullable=False)


class UserWord(Base):
    __tablename__ = "users_words"

    user_id = sq.Column(
        sq.Integer,
        sq.ForeignKey("users.user_id"),
        primary_key=True,
    )
    target_word = sq.Column(
        sq.String(length=50),
        sq.ForeignKey("words.target_word"),
        primary_key=True,
    )
    correct_answers = sq.Column(sq.Integer, default=0, nullable=False)
    wrong_answers = sq.Column(sq.Integer, default=0, nullable=False)

    user = relationship("User", backref="user_word")
    word = relationship("Word", backref="user_word")


class DbModel:

    def __init__(
        self,
        login: str,
        password: str,
        db_name="postgres",
        server="localhost",
        port=5432,
        db_adapter="psycopg",
    ) -> None:
        self.db_name = db_name
        self._server = server
        self._port = port
        self._adapter = db_adapter
        self.engine = self._create_engine(login, password)
        self.Session = sessionmaker(self.engine)

    def word_is_exist(self, db_word: str) -> bool:
        with self.Session() as ses:
            it_exist = ses.query(
                sq.exists().where(Word.target_word == db_word),
            ).scalar()
        return it_exist

    def user_is_exist(self, user_id: int) -> bool:
        with self.Session() as ses:
            it_exist = ses.query(
                sq.exists().where(User.user_id == user_id),
            ).scalar()
        return it_exist

    def user_word_is_exist(self, user_id: int, db_word: str) -> bool:
        with self.Session() as ses:
            it_exist = ses.query(
                sq.exists().where(
                    sq.and_(
                        UserWord.user_id == user_id,
                        UserWord.target_word == db_word,
                    ),
                ),
            ).scalar()
        return it_exist

    def add_data_to_db(self, *args):
        with self.Session() as ses:
            ses.add_all(args)
            ses.commit()

    def delete_word(self, user_id: int, dict_word: str):
        with self.Session() as ses:
            user_word = (
                ses.query(UserWord)
                .filter(
                    sq.and_(
                        UserWord.user_id == user_id,
                        UserWord.target_word == dict_word,
                    ),
                )
                .one()
            )
            ses.delete(user_word)
            ses.commit()

    def update_user_word(self, user_id: int, dict_word: DictWord):
        user_word = UserWord(
            user_id=user_id,
            target_word=dict_word.target_word,
            correct_answers=dict_word.correct_answers,
            wrong_answers=dict_word.wrong_answers,
        )
        with self.Session() as ses:
            user_word = ses.query(UserWord).get(
                (user_id, dict_word.target_word),
            )
            user_word.correct_answers = dict_word.correct_answers
            user_word.wrong_answers = dict_word.wrong_answers
            ses.add(user_word)
            ses.commit()

    def get_all_user_words(self, user_id: int) -> list[DictWord]:
        with self.Session() as ses:
            user_words = (
                ses.query(UserWord)
                .join(Word)
                .filter(UserWord.user_id == user_id)
            ).all()
            dict_words = []
            for user_word in user_words:
                dict_words.append(self._create_dict_word(user_word))
        return dict_words

    def create_all_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_all_table(self) -> None:
        Base.metadata.drop_all(self.engine)

    def _create_engine(self, login: str, password: str) -> sq.Engine:
        dsn = (
            f"postgresql+{self._adapter}://{login}:{password}@"
            f"{self._server}:{self._port}/{self.db_name}"
        )
        return sq.create_engine(url=dsn)

    @staticmethod
    def _create_dict_word(user_word: Any) -> DictWord:
        dict_word: DictWord = user_word.word.dict_word
        dict_word.correct_answers = user_word.correct_answers
        dict_word.wrong_answers = user_word.wrong_answers
        return dict_word


if __name__ == "__main__":
    import os

    db = DbModel(
        login=os.environ["LOGIN_DB"],
        password=os.environ["PASSWORD_DB"],
        db_name="tg_bot_db",
    )
    # db.drop_all_table()
    # db.create_all_tables()
    # db.delete_word(843771109, "КОШКА")
    # print(db.user_word_is_exist(843771109, "КОШКА"))

    for word in db.get_all_user_words(843771109):
        print(
            word.target_word,
            word.translate_word,
            word.other_words,
            word.correct_answers,
            word.wrong_answers,
        )
