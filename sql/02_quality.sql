CREATE OR REPLACE VIEW quality_checks AS
 
-- 1. Invoice total equals the sum of its lines (exact, DECIMAL arithmetic)
SELECT
    'invoice_total_matches_lines'                      AS check_name,
    count(*) FILTER (WHERE i.total <> l.lines_total)   AS failed_rows,
    count(*)                                           AS checked_rows
FROM stg_invoice AS i
JOIN (
    SELECT invoice_id, sum(line_total) AS lines_total
    FROM stg_invoice_line
    GROUP BY invoice_id
) AS l USING (invoice_id)
 
UNION ALL
-- 2. Every invoice has at least one line (check 1 would silently skip those)
SELECT
    'invoice_has_lines',
    count(*) FILTER (WHERE l.invoice_id IS NULL),
    count(*)
FROM stg_invoice AS i
LEFT JOIN (SELECT DISTINCT invoice_id FROM stg_invoice_line) AS l USING (invoice_id)
 
UNION ALL
-- 3. Every invoice line points to an existing invoice
SELECT
    'line_has_invoice',
    count(*) FILTER (WHERE i.invoice_id IS NULL),
    count(*)
FROM stg_invoice_line AS l
LEFT JOIN stg_invoice AS i USING (invoice_id)
 
UNION ALL
-- 4. Every invoice line points to an existing track
SELECT
    'line_has_track',
    count(*) FILTER (WHERE t.track_id IS NULL),
    count(*)
FROM stg_invoice_line AS l
LEFT JOIN stg_track AS t USING (track_id)