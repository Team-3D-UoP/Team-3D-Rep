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


def search_registered_parts_by_attributes(
    brand: Optional[str] = None,
    year: Optional[str] = None,
    part_name: Optional[str] = None,
    db_path: str = DB_PATH,
) -> List[Dict[str, Any]]:
    query = """
    SELECT
        rps.*
    FROM RegisteredParts AS rps
    WHERE
        rps.brand LIKE :brand
        AND rps.year LIKE :year
        AND rps.part_name LIKE :part_name;
    """
    params = {
        "brand": f"%{brand}%" if brand else "%",
        "year": f"%{year}%" if year else "%",
        "part_name": f"%{part_name}%" if part_name else "%",
    }
    with connect_db(db_path) as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    print("\n--- Search for Parts by Attributes ---")
    brand = input("Enter part brand (or press Enter to skip): ") or None
    year = input("Enter part year (or press Enter to skip): ") or None
    part_name = input("Enter part name (or press Enter to skip): ") or None
    print(f"\nParts matching brand '{brand}', year '{year}', and part name '{part_name}':")
    print(search_registered_parts_by_attributes(brand=brand, year=year, part_name=part_name))
