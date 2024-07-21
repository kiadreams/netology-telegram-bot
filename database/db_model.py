import os

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


class Word(Base):
    """The class describes a table of words in the database."""

    __tablename__ = "words"

    target_word = sq.Column(sq.String(length=50), primary_key=True)
    translate_word = sq.Column(sq.String(length=50), nullable=False)
    another_word1 = sq.Column(sq.String(length=50), nullable=True)
    another_word2 = sq.Column(sq.String(length=50), nullable=True)
    another_word3 = sq.Column(sq.String(length=50), nullable=True)


class User(Base):
    """The class describes the user table in the database."""

    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=50), nullable=False)
    last_name = sq.Column(sq.String(length=50), nullable=False)


class UserWord(Base):
    """The class describes a table of user words in the database."""

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
    """The class describes the functionality of the database."""

    def __init__(
        self,
        login: str,
        password: str,
        db_name="postgres",
        server="localhost",
        port=5432,
        db_adapter="psycopg",
    ) -> None:
        """Set database connection parameters.

        :param login: login to connect to the database
        :param password: password to connect to the database
        :param db_name: database name
        :param server: database connection server
        :param port: database connection port
        :param db_adapter: adapter for connecting to the database
        """
        self.db_name = db_name
        self._server = server
        self._port = port
        self._adapter = db_adapter
        self.engine = self._create_engine(login, password)
        self.Session = sessionmaker(self.engine)

    def get_db_word(self, target_word: str) -> Word:
        """Get a word entry from the word table by the specified value."""
        with self.Session() as ses:
            db_word = ses.query(Word).get(target_word)
        return db_word

    def get_words(self, user_id: int):
        with self.Session() as ses:
            words = (
                ses.query(Word.target_word, Word.translate_word)
                .join(UserWord, isouter=True)
                .where(UserWord.user_id.in_([user_id, None]))
                .order_by(sq.func.random())
                .limit(4)
                .all()
            )
        return words

    def word_is_not_exist(self, target_word: str) -> bool:
        """Check if there is no entry in the word table."""
        with self.Session() as ses:
            it_exist = ses.query(
                sq.exists().where(Word.target_word == target_word),
            ).scalar()
        return not it_exist

    def user_is_not_exist(self, user_id: int) -> bool:
        """Check the absence of an entry in the user table."""
        with self.Session() as ses:
            it_exist = ses.query(
                sq.exists().where(User.user_id == user_id),
            ).scalar()
        return not it_exist

    def user_words_table_is_empty(self) -> bool:
        """Check the absence of an entry in the user table."""
        with self.Session() as ses:
            is_table_empty = ses.query(UserWord).all()
        return not is_table_empty

    def words_table_is_empty(self) -> bool:
        """Check the absence of an entry in the word table."""
        with self.Session() as ses:
            is_table_empty = ses.query(Word).all()
        return not is_table_empty

    def user_word_is_not_exist(self, user_id: int, target_word: str) -> bool:
        """Check if there is no entry in the user's word table."""
        with self.Session() as ses:
            it_exist = ses.query(
                sq.exists().where(
                    sq.and_(
                        UserWord.user_id == user_id,
                        UserWord.target_word == target_word,
                    ),
                ),
            ).scalar()
        return not it_exist

    def add_user_to_db(self, user_id: int, first_name: str, last_name: str):
        """Add a user to the user table."""
        if self.user_is_not_exist(user_id):
            user = User(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
            )
            with self.Session() as ses:
                ses.add(user)
                ses.commit()

    def add_word_to_db(self, target_word: str, translate_word: str):
        """Add a word to the word table."""
        if self.word_is_not_exist(target_word):
            word = Word(
                target_word=target_word,
                translate_word=translate_word,
            )
            with self.Session() as ses:
                ses.add(word)
                ses.commit()

    def add_user_word_to_db(self, user_id: int, target_word: str):
        """Add a word to a specific user."""
        if self.user_word_is_not_exist(user_id, target_word):
            user_word = UserWord(user_id=user_id, target_word=target_word)
            with self.Session() as ses:
                ses.add(user_word)
                ses.commit()

    def delete_word(self, user_id: int, dict_word: str):
        """Delete a word from a user."""
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
            if user_word:
                ses.delete(user_word)
            ses.commit()

    def update_user_word(
        self,
        user_id: int,
        word: str,
        corr_answers=0,
        wrong_answers=0,
    ) -> None:
        """Update the entry about the specified user's word."""
        with self.Session() as ses:
            user_word = ses.query(UserWord).get(
                (user_id, word),
            )
            user_word.correct_answers += corr_answers
            user_word.wrong_answers += wrong_answers
            ses.add(user_word)
            ses.commit()

    def get_num_of_user_words(self, user_id: int) -> int:
        """Return the number of user's words.

        :param user_id:
        :return:
        """
        with self.Session() as ses:
            number = ses.query(UserWord).count()
            ses.commit()
        return number

    def create_all_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_all_table(self) -> None:
        Base.metadata.drop_all(self.engine)

    def _create_engine(self, login: str, password: str) -> sq.Engine:
        """Create a driver for working with the database.

        :param login: login to connect to the database
        :param password: password to connect to the database
        :return:
        """
        dsn = (
            f"postgresql+{self._adapter}://{login}:{password}@"
            f"{self._server}:{self._port}/{self.db_name}"
        )
        return sq.create_engine(url=dsn)


if __name__ == "__main__":
    db_model = DbModel(
        login=os.environ["LOGIN_DB"],
        password=os.environ["PASSWORD_DB"],
        db_name=os.environ["DB_NAME"],
    )

    # result = db_model.get_words(843_771_109)
    # print(result)
    # print(db_model.user_is_not_exist(843_771_109))

    db_model.drop_all_table()
    db_model.create_all_tables()
