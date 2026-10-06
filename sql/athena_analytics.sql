-- Tenant-scoped daily transaction metrics over the curated Glue table.
SELECT tenant_id,
       event_date,
       event_type,
       COUNT(*) AS transaction_count,
       SUM(amount) AS total_amount,
       AVG(amount) AS average_amount
FROM curated_transactions
WHERE tenant_id = 'bank-demo-01'
  AND event_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31'
GROUP BY 1,2,3
ORDER BY 2,3;

-- Data-quality reconciliation: records with unsupported currency values.
SELECT tenant_id, currency, COUNT(*) AS invalid_rows
FROM curated_transactions
WHERE currency NOT IN ('USD','CAD','EUR','GBP')
GROUP BY 1,2;
