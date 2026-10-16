# KPI definitions

Data: Chinook sample database (digital music store), 2021-01-01 to 2025-12-22.
All KPIs read from the staging views and are implemented in `sql/03_kpis.sql`.
Revenue figures are in the currency of the source data.

## KPI 1: Revenue per year
- **Business question:** How does yearly revenue develop, and is it growing?
- **Definition:** sum of `stg_invoice.total` per `invoice_year`. Also number of
  invoices, distinct customers, average invoice value and year-over-year change
  in percent: (revenue - previous year revenue) / previous year revenue * 100.
- **Source views:** `stg_invoice`
- **View:** `kpi_revenue_by_year`
- **Known limits:**
  - Only 5 years of data, so a trend is hard to separate from noise.
  - The first year has no year-over-year value.
  - Years end on slightly different dates (see `last_invoice_date`; 2025 ends
    on 22 December), so the last year is not perfectly comparable.
  - It is a sample database, not a real business.
- **Chart file:** `docs/img/revenue_by_year.png`

## KPI 2: Revenue by genre
- **Business question:** Which genres bring the most revenue, and how
  concentrated is revenue in a few genres?
- **Definition:** sum of `line_total` per genre, plus units sold, distinct
  tracks sold, share of total revenue, rank and cumulative share (genres
  ordered from highest to lowest revenue).
- **Source views:** `stg_invoice_line`, `stg_track`
- **View:** `kpi_revenue_by_genre`
- **Known limits:**
  - Only genres with at least one sale appear in the view.
  - Each track has exactly one genre, so a track cannot count for two genres.
  - Genres tied on revenue get the same rank (`rank()`).
- **Chart file:** `docs/img/revenue_by_genre.png`

## KPI 3: Revenue by artist
- **Business question:** Which artists bring the most revenue?
- **Definition:** sum of `line_total` per artist (track -> album -> artist),
  plus units sold, distinct albums and tracks sold, share of total and rank.
- **Source views:** `stg_invoice_line`, `stg_track`, `stg_album`, `stg_artist`
- **View:** `kpi_revenue_by_artist`
- **Known limits:**
  - Only artists with at least one sale appear (not every artist in the catalog).
  - Many artists have few sales at a price of about 1 per track, so many tie
    on revenue and ranks are coarse.
  - Shares are rounded per row, so they can add up to slightly more than 100.
  - Compilations or "various artists" entries count as one artist.
- **Chart file:** `docs/img/top10_artists.png`

## Reconciliation
Revenue in each KPI view adds up to the same total as the invoices and the
invoice lines. This is checked in `tests/test_sql.py`.