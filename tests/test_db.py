import os

import pytest
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from database.db_model import DbModel

Session = sessionmaker()


class TestClass:
    login = os.environ["LOGIN_DB"]
    password = os.environ["PASSWORD_DB"]
    db_name = "test_db"
    DSN = None
    model: DbModel = None

    @classmethod
    def setup_class(cls):
        cls.DSN = (
            f"postgresql+psycopg://{cls.login}:{cls.password}@"
            f"localhost:5432/{cls.db_name}"
        )
        if not database_exists(cls.DSN):
            create_database(cls.DSN)

    def test_db_is_exists(self):
        assert database_exists(self.DSN)

    def test_create_model(self):
        TestClass.model = DbModel(self.login, self.password, self.db_name)
        assert isinstance(self.model, DbModel)

    @pytest.mark.parametrize("table_name", ("users", "users_words", "words"))
    def test_is_tables_exists(self, table_name):
        engine = sq.create_engine(TestClass.DSN)
        some_inspect = sq.inspect(engine)
        assert not some_inspect.has_table(table_name)

    @pytest.mark.parametrize("table_name", ("users", "users_words", "words"))
    def test_created_all_tables(self, table_name):
        engine = sq.create_engine(TestClass.DSN)
        some_inspect = sq.inspect(engine)
        self.model.create_all_tables()
        assert some_inspect.has_table(table_name)

    @pytest.mark.parametrize(
        "user_id, expected",
        [(12345, False), (67894, False), (34334345, True)],
    )
    def test_check_users(self, user_id: int, expected: bool):
        users = [
            (12345, "Valera", "Korshunov"),
            (67894, "Mihail", "Ignatovich"),
        ]
        for user in users:
            self.model.add_user_to_db(*user)
        is_exist = self.model.user_is_not_exist(user_id)
        assert is_exist == expected

    @pytest.mark.parametrize("table_name", ("users", "users_words", "words"))
    def test_drop_all_tables(self, table_name):
        engine = sq.create_engine(TestClass.DSN)
        some_inspect = sq.inspect(engine)
        self.model.drop_all_table()
        assert not some_inspect.has_table(table_name)

    @classmethod
    def teardown_class(cls):
        if database_exists(cls.DSN):
            drop_database(cls.DSN)
