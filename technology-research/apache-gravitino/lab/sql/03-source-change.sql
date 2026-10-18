-- Safe to repeat. Observe this column through the Gravitino metadata API.
ALTER TABLE sales.orders ADD COLUMN IF NOT EXISTS source_note TEXT;
UPDATE sales.orders SET source_note = 'changed at source' WHERE id = 1;
