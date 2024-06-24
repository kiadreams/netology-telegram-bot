import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class Clients(Base):
    __tablename__ = "clients"

    client_id = sq.Column(sq.Integer, primary_key=True)

    user = relationship("ListType", backref="client", cascade="all, delete")


class Users(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=50), nullable=False)
    last_name = sq.Column(sq.String(length=50), nullable=False)
    prf_link = sq.Column(sq.Text, nullable=False)

    client = relationship("ListType", backref="user", cascade="all, delete")

    photo = relationship("Photos", backref="user", cascade="all, delete")


class ListType(Base):
    __tablename__ = "list_type"

    client_id = sq.Column(
        sq.Integer,
        sq.ForeignKey("clients.client_id"),
        primary_key=True,
        nullable=False,
    )
    user_id = sq.Column(
        sq.Integer,
        sq.ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False,
    )
    blacklist = sq.Column(sq.Boolean, default=False, nullable=False)


class Photos(Base):
    __tablename__ = "photos"

    photo_id = sq.Column(sq.Integer, primary_key=True)
    owner_id = sq.Column(
        sq.Integer,
        sq.ForeignKey(Users.user_id),
        primary_key=True,
        nullable=False,
    )
    photo_link = sq.Column(sq.Text, nullable=False)
    user_mark = sq.Column(sq.Boolean, default=False, nullable=False)

    # Define a relationship with Users:

    def __str__(self) -> str:
        return f"{self.photo_id=} {self.owner_id=}"


class ModelDb:

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

    def _create_engine(self, login: str, password: str) -> sq.Engine:
        dsn = (
            f"postgresql+{self._adapter}://{login}:{password}@"
            f"{self._server}:{self._port}/{self.db_name}"
        )
        return sq.create_engine(url=dsn)

    def write_users_to_db(
        self,
        user: Users,
        client: Clients,
        photos: list[Photos],
        blacklisted: bool,
    ):
        list_t = ListType(
            user_id=user.user_id,
            blacklist=blacklisted,
            client_id=client.client_id,
        )
        with self.Session() as s:
            try:
                s.add(client)
                s.commit()
            except IntegrityError:
                s.rollback()
                try:
                    s.add(user)
                    s.commit()
                except IntegrityError:
                    s.rollback()
                    s.add(list_t)
                    s.commit()
                else:
                    s.add_all([list_t, *photos])
                    s.commit()
            else:
                s.add_all([client, user, list_t, *photos])
                s.commit()

    def download_users(
        self, client_id: int, blacklisted: bool,
    ) -> dict[Users : list[Photos]]:
        users = {}
        with self.Session() as s:
            qr = (
                s.query(Users, Photos)
                .join(ListType)
                .outerjoin(Photos)
                .filter(
                    sq.and_(
                        ListType.blacklist == blacklisted,
                        ListType.client_id == client_id,
                    )
                )
                .all()
            )
            for user, photo in qr:
                users.setdefault(user, []).append(photo)
            return users

    def create_all_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_all_table(self) -> None:
        Base.metadata.drop_all(self.engine)


if __name__ == "__main__":
    import os

    model = ModelDb(
        login=os.environ["LOGIN_DB"],
        password=os.environ["PASSWORD_DB"],
        db_name="vk_bot_db",
    )
    model.drop_all_table()
    model.create_all_tables()
