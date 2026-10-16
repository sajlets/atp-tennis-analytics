-- KPI 1: revenue per year, with year-over-year change
CREATE OR REPLACE VIEW kpi_revenue_by_year AS
WITH yearly AS (
    SELECT
        invoice_year,
        count(*)                       AS invoices,
        count(DISTINCT customer_id)    AS customers,
        sum(total)                     AS revenue,
        min(CAST(invoice_ts AS DATE))  AS first_invoice_date,
        max(CAST(invoice_ts AS DATE))  AS last_invoice_date
    FROM stg_invoice
    GROUP BY invoice_year
)
SELECT
    invoice_year,
    invoices,
    customers,
    revenue,
    round(revenue / invoices, 2)       AS avg_invoice_value,
    first_invoice_date,
    last_invoice_date,
    round(100.0 * (revenue - lag(revenue) OVER (ORDER BY invoice_year))
          / lag(revenue) OVER (ORDER BY invoice_year), 2) AS revenue_yoy_pct
FROM yearly
ORDER BY invoice_year;
 
 
-- KPI 2: revenue by genre, with share, rank and cumulative share
CREATE OR REPLACE VIEW kpi_revenue_by_genre AS
WITH by_genre AS (
    SELECT
        t.genre_name,
        sum(l.line_total)          AS revenue,
        sum(l.quantity)            AS units_sold,
        count(DISTINCT l.track_id) AS tracks_sold
    FROM stg_invoice_line AS l
    JOIN stg_track        AS t USING (track_id)
    GROUP BY t.genre_name
)
SELECT
    genre_name,
    revenue,
    units_sold,
    tracks_sold,
    round(100.0 * revenue / sum(revenue) OVER (), 2)  AS revenue_share_pct,
    rank() OVER (ORDER BY revenue DESC)               AS revenue_rank,
    round(100.0 * sum(revenue) OVER (
              ORDER BY revenue DESC, genre_name
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / sum(revenue) OVER (), 2)                  AS cumulative_share_pct
FROM by_genre
ORDER BY revenue_rank, genre_name;
 
 
-- KPI 3: revenue by artist, with share and rank
CREATE OR REPLACE VIEW kpi_revenue_by_artist AS
WITH by_artist AS (
    SELECT
        a.artist_name,
        sum(l.line_total)          AS revenue,
        sum(l.quantity)            AS units_sold,
        count(DISTINCT t.album_id) AS albums_sold,
        count(DISTINCT l.track_id) AS tracks_sold
    FROM stg_invoice_line AS l
    JOIN stg_track        AS t  USING (track_id)
    JOIN stg_album        AS al USING (album_id)
    JOIN stg_artist       AS a  USING (artist_id)
    GROUP BY a.artist_name
)
SELECT
    artist_name,
    revenue,
    units_sold,
    albums_sold,
    tracks_sold,
    round(100.0 * revenue / sum(revenue) OVER (), 2)  AS revenue_share_pct,
    rank() OVER (ORDER BY revenue DESC)               AS revenue_rank
FROM by_artist
ORDER BY revenue_rank, artist_name;
 