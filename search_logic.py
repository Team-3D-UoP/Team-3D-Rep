import sqlite3
from typing import Any, Dict, List, Optional

DB_PATH = "database.db"


def connect_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def search_cars_by_keyword(term: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    query = """
    SELECT
        rcs.CarID,
        rcs.make,
        rcs.model,
        rcs.year,
        rcs.license,
        rcs.engine,
        rcs.wheels,
        u.UserID AS owner_userid,
        u.username AS owner_username,
        u.email AS owner_email
    FROM RegisteredCars AS rcs
    LEFT JOIN CarOwners AS ca ON rcs.CarID = ca.CarID
    LEFT JOIN Users AS u ON ca.UserID = u.UserID
    WHERE
        rcs.make LIKE :term
        OR rcs.model LIKE :term
        OR rcs.year LIKE :term
        OR rcs.license LIKE :term
        OR rcs.engine LIKE :term
        OR rcs.wheels LIKE :term;
    """
    params = {"term": f"%{term}%"}
    with connect_db(db_path) as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def search_by_owner(owner_term: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    query = """
    SELECT
        rcs.CarID,
        rcs.make,
        rcs.model,
        rcs.year,
        rcs.license,
        rcs.engine,
        rcs.wheels,
        u.UserID AS owner_userid,
        u.username AS owner_username,
        u.email AS owner_email
    FROM RegisteredCars AS rcs
    JOIN CarOwners AS ca ON rcs.CarID = ca.CarID
    JOIN Users AS u ON ca.UserID = u.UserID
    WHERE
        u.username LIKE :ownerTerm
        OR u.email LIKE :ownerTerm;
    """
    params = {"ownerTerm": f"%{owner_term}%"}
    with connect_db(db_path) as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def search_cars_year_range(
    min_year: int,
    max_year: int,
    model_filter: Optional[str] = None,
    make_filter: Optional[str] = None,
    db_path: str = DB_PATH,
) -> List[Dict[str, Any]]:
    query = """
    SELECT
        rcs.CarID,
        rcs.make,
        rcs.model,
        rcs.year,
        rcs.license,
        rcs.engine,
        rcs.wheels
    FROM RegisteredCars AS rcs
    WHERE
        CAST(rcs.year AS INTEGER) BETWEEN :minYear AND :maxYear
        AND rcs.model LIKE :modelFilter
        AND rcs.make LIKE :makeFilter;
    """
    params = {
        "minYear": min_year,
        "maxYear": max_year,
        "modelFilter": f"%{model_filter}%" if model_filter else "%",
        "makeFilter": f"%{make_filter}%" if make_filter else "%",
    }
    with connect_db(db_path) as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def search_registered_parts(
    min_price: float,
    max_price: float,
    name_filter: Optional[str] = None,
    db_path: str = DB_PATH,
) -> List[Dict[str, Any]]:
    query = """
    SELECT
        rps.*
    FROM RegisteredParts AS rps
    WHERE
        rps.price BETWEEN :minPrice AND :maxPrice
        OR rps.part_name LIKE :nameFilter;
    """
    params = {
        "minPrice": min_price,
        "maxPrice": max_price,
        "nameFilter": f"%{name_filter}%" if name_filter else "%",
    }
    with connect_db(db_path) as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    print("Example search results:\n")
    print("Cars matching 'Toyota':")
    print(search_cars_by_keyword("Toyota"))
    print("\nCars owned by users matching 'gmail.com':")
    print(search_by_owner("gmail.com"))
    print("\nCars in year range 2024-2026, make filter 'Toyota':")
    print(search_cars_year_range(2024, 2026, make_filter="Toyota"))
    print("\nParts priced between 20 and 100:")
    print(search_registered_parts(20.0, 100.0, name_filter="Filter"))
