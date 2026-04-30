from sqlalchemy import Integer, cast, or_, select
from models import db


class User(db.Model):
    __tablename__ = 'Users'

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)

    owned_cars = db.relationship('CarOwner', back_populates='user')


class RegisteredCar(db.Model):
    __tablename__ = 'RegisteredCars'

    CarID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    license = db.Column(db.String, nullable=False, unique=True)
    engine = db.Column(db.String)
    wheels = db.Column(db.String)

    owner_link = db.relationship('CarOwner', back_populates='car', uselist=False)


class CarOwner(db.Model):
    __tablename__ = 'CarOwners'

    CarID = db.Column(db.Integer, db.ForeignKey('RegisteredCars.CarID'), primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)

    car = db.relationship('RegisteredCar', back_populates='owner_link')
    user = db.relationship('User', back_populates='owned_cars')


class RegisteredPart(db.Model):
    __tablename__ = 'RegisteredParts'

    PartID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    brand = db.Column(db.String)
    year = db.Column(db.String)
    part_name = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String)
    image = db.Column(db.String)


def _get_session(session=None):
    return session or db.session


def search_cars_by_keyword(term: str, session=None):
    """Search cars using make, model, year, license, engine, and wheels."""
    session = _get_session(session)
    stmt = (
        select(
            RegisteredCar.CarID,
            RegisteredCar.make,
            RegisteredCar.model,
            RegisteredCar.year,
            RegisteredCar.license,
            RegisteredCar.engine,
            RegisteredCar.wheels,
            User.UserID.label('owner_userid'),
            User.username.label('owner_username'),
            User.email.label('owner_email'),
        )
        .outerjoin(CarOwner, RegisteredCar.CarID == CarOwner.CarID)
        .outerjoin(User, User.UserID == CarOwner.UserID)
        .where(
            or_(
                RegisteredCar.make.like(term),
                RegisteredCar.model.like(term),
                RegisteredCar.year.like(term),
                RegisteredCar.license.like(term),
                RegisteredCar.engine.like(term),
                RegisteredCar.wheels.like(term),
            )
        )
    )

    return session.execute(stmt).mappings().all()


def search_by_owner(owner_term: str, session=None):
    """Search cars by owner username or email."""
    session = _get_session(session)
    stmt = (
        select(
            RegisteredCar.CarID,
            RegisteredCar.make,
            RegisteredCar.model,
            RegisteredCar.year,
            RegisteredCar.license,
            RegisteredCar.engine,
            RegisteredCar.wheels,
            User.UserID.label('owner_userid'),
            User.username.label('owner_username'),
            User.email.label('owner_email'),
        )
        .join(CarOwner, RegisteredCar.CarID == CarOwner.CarID)
        .join(User, User.UserID == CarOwner.UserID)
        .where(
            or_(
                User.username.like(owner_term),
                User.email.like(owner_term),
            )
        )
    )

    return session.execute(stmt).mappings().all()


def search_by_year_range(
    min_year: int,
    max_year: int,
    model_filter: str = '%',
    make_filter: str = '%',
    session=None,
):
    """Search registered cars by year range and optional make/model filters."""
    session = _get_session(session)
    stmt = select(
        RegisteredCar.CarID,
        RegisteredCar.make,
        RegisteredCar.model,
        RegisteredCar.year,
        RegisteredCar.license,
        RegisteredCar.engine,
        RegisteredCar.wheels,
    ).where(
        cast(RegisteredCar.year, Integer).between(min_year, max_year),
        RegisteredCar.model.like(model_filter),
        RegisteredCar.make.like(make_filter),
    )

    return session.execute(stmt).mappings().all()


def search_parts_by_price(
    min_price: float,
    max_price: float,
    name_filter: str = '%',
    session=None,
):
    """Search registered parts by price range or name filter."""
    session = _get_session(session)
    stmt = select(RegisteredPart).where(
        RegisteredPart.price.between(min_price, max_price)
        | RegisteredPart.part_name.like(name_filter)
    )

    return session.execute(stmt).mappings().all()
