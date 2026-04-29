-- search_logic.sql
-- Reusable queries for Database1.sql 

-- Search cars by keyword across make, model, year, license, engine, wheels
--   Use :term such as '%Toyota%', '%Hybrid%' or %2025%.
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

-- e.g., SELECT * FROM RegisteredCars WHERE make LIKE '%Toyota%';

-- Search by owner username/email
--    Use :ownerTerm such as '%olivergrant%' or '%gmail.com%'.
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

-- Search by year range and optional make/model filters
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

-- Search registered parts by price range
--    :minPrice and :maxPrice.
SELECT
    rps.*
FROM RegisteredParts AS rps
WHERE
    rps.price BETWEEN :minPrice AND :maxPrice
    OR rps.name LIKE :nameFilter;