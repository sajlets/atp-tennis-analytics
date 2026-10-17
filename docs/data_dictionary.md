# Data dictionary

Source: Chinook sample database (digital music store), loaded 1:1 into DuckDB as `raw_<table>` tables by `src/load.py`. Staging views in `sql/01_staging.sql` rename columns to snake_case and fix types. The tables below describe the staging views. `Nulls` is the number of empty values in the column.

Raw tables used only for checks or joins: `raw_customer` (customer existence check), `raw_genre` (genre names). Other source tables (employee, playlist, media type, playlist track) are loaded but not used by the KPIs.

## stg_invoice

Built from `raw_invoice`. Rows: 412 (raw: 412).

| Column | Type | Meaning | Nulls |
|---|---|---|---|
| invoice_id | BIGINT | Unique invoice id (primary key) | 0 |
| customer_id | BIGINT | Customer who was billed (matches Customer.CustomerId) | 0 |
| invoice_ts | TIMESTAMP | Invoice date and time. Raw value is text, cast to TIMESTAMP | 0 |
| invoice_year | BIGINT | Calendar year of invoice_ts | 0 |
| billing_country | VARCHAR | Country on the invoice | 0 |
| total | DECIMAL(10,2) | Invoice total. Raw value is DOUBLE, cast to DECIMAL(10,2) | 0 |

## stg_invoice_line

Built from `raw_invoiceline`. Rows: 2240 (raw: 2240).

| Column | Type | Meaning | Nulls |
|---|---|---|---|
| invoice_line_id | BIGINT | Unique line id (primary key) | 0 |
| invoice_id | BIGINT | Invoice this line belongs to | 0 |
| track_id | BIGINT | Track that was sold | 0 |
| unit_price | DECIMAL(10,2) | Price per unit. Raw value is DOUBLE, cast to DECIMAL(10,2) | 0 |
| quantity | BIGINT | Number of units sold | 0 |
| line_total | DECIMAL(29,2) | unit_price * quantity, exact DECIMAL arithmetic | 0 |

## stg_track

Built from `raw_track`. Rows: 3503 (raw: 3503).

| Column | Type | Meaning | Nulls |
|---|---|---|---|
| track_id | BIGINT | Unique track id (primary key) | 0 |
| track_name | VARCHAR | Track title | 0 |
| album_id | BIGINT | Album the track belongs to | 0 |
| media_type_id | BIGINT | Media type id (file format) | 0 |
| genre_id | BIGINT | Genre id | 0 |
| genre_name | VARCHAR | Genre name, added by LEFT JOIN to raw_genre | 0 |
| composer | VARCHAR | Composer(s) as free text | 977 |
| milliseconds | BIGINT | Track length in milliseconds | 0 |
| bytes | BIGINT | File size in bytes | 0 |
| unit_price | DECIMAL(10,2) | List price per unit, cast to DECIMAL(10,2) | 0 |

## stg_album

Built from `raw_album`. Rows: 347 (raw: 347).

| Column | Type | Meaning | Nulls |
|---|---|---|---|
| album_id | BIGINT | Unique album id (primary key) | 0 |
| album_title | VARCHAR | Album title | 0 |
| artist_id | BIGINT | Artist who made the album | 0 |

## stg_artist

Built from `raw_artist`. Rows: 275 (raw: 275).

| Column | Type | Meaning | Nulls |
|---|---|---|---|
| artist_id | BIGINT | Unique artist id (primary key) | 0 |
| artist_name | VARCHAR | Artist name. TV series also appear here | 0 |

## Cleaning rules applied in staging

- Column names renamed from PascalCase to snake_case.
- `InvoiceDate` converted from text to TIMESTAMP; `invoice_year` derived from it.
- Prices and totals converted from DOUBLE to DECIMAL(10,2). Comparing invoice totals with line sums on DOUBLE gave 56 false mismatches from rounding; on DECIMAL there are none.
- `line_total` is calculated from the DECIMAL price, so sums are exact.
- Genre name added to tracks with a LEFT JOIN, so no track can be lost.
- No rows are removed or changed: row counts in staging equal the raw tables.