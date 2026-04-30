import sqlite3
from typing import Any, Dict, List, Optional


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_connection(db_path: str, row_factory: Optional[sqlite3.Row] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = row_factory or dict_factory
    return conn


def search_cars_by_keyword(conn: sqlite3.Connection, term: str) -> List[Dict[str, Any]]:
    """Search cars by keyword across make, model, year, license, engine, and wheels."""
    sql = """
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
    cursor = conn.execute(sql, {"term": term})
    return cursor.fetchall()


def search_by_owner(conn: sqlite3.Connection, owner_term: str) -> List[Dict[str, Any]]:
    """Search cars by owner username or email."""
    sql = """
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
    cursor = conn.execute(sql, {"ownerTerm": owner_term})
    return cursor.fetchall()


def search_by_year_range(
    conn: sqlite3.Connection,
    min_year: int,
    max_year: int,
    model_filter: str = "%",
    make_filter: str = "%",
) -> List[Dict[str, Any]]:
    """Search registered cars by year range and optional make/model filters."""
    sql = """
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
        "modelFilter": model_filter,
        "makeFilter": make_filter,
    }
    cursor = conn.execute(sql, params)
    return cursor.fetchall()


def search_parts_by_price(
    conn: sqlite3.Connection,
    min_price: float,
    max_price: float,
    name_filter: str = "%",
) -> List[Dict[str, Any]]:
    """Search registered parts by price range or name filter."""
    sql = """
    SELECT
        rps.*
    FROM RegisteredParts AS rps
    WHERE
        rps.price BETWEEN :minPrice AND :maxPrice
        OR rps.name LIKE :nameFilter;
    """
    cursor = conn.execute(sql, {
        "minPrice": min_price,
        "maxPrice": max_price,
        "nameFilter": name_filter,
    })
    return cursor.fetchall()