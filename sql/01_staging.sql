CREATE OR REPLACE VIEW stg_invoice AS
SELECT
    InvoiceId                            AS invoice_id,
    CustomerId                           AS customer_id,
    CAST(InvoiceDate AS TIMESTAMP)       AS invoice_ts,
    year(CAST(InvoiceDate AS TIMESTAMP)) AS invoice_year,
    BillingCountry                       AS billing_country,
    CAST(Total AS DECIMAL(10, 2))        AS total
FROM raw_invoice;

CREATE OR REPLACE VIEW stg_invoice_line AS
SELECT
    InvoiceLineId                                   AS invoice_line_id,
    InvoiceId                                       AS invoice_id,
    TrackId                                         AS track_id,
    CAST(UnitPrice AS DECIMAL(10, 2))               AS unit_price,
    Quantity                                        AS quantity,
    CAST(UnitPrice AS DECIMAL(10, 2)) * Quantity    AS line_total
FROM raw_invoiceline;

CREATE OR REPLACE VIEW stg_track AS
SELECT
    t.TrackId                            AS track_id,
    t.Name                               AS track_name,
    t.AlbumId                            AS album_id,
    t.MediaTypeId                        AS media_type_id,
    t.GenreId                            AS genre_id,
    g.Name                               AS genre_name,
    t.Composer                           AS composer,
    t.Milliseconds                       AS milliseconds,
    t.Bytes                              AS bytes,
    CAST(t.UnitPrice AS DECIMAL(10, 2))  AS unit_price
FROM raw_track AS t
LEFT JOIN raw_genre AS g ON g.GenreId = t.GenreId;