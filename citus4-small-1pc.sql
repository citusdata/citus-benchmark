\set scale 5000
\set aid1 random(1, 100000 * :scale)
\set aid2 random(1, 100000 * :scale)
\set delta random(-5000, 5000)
BEGIN;
UPDATE citus4_small_accounts1 SET abalance = abalance + :delta WHERE aid = :aid1;
UPDATE citus4_small_accounts2 SET abalance = abalance - :delta WHERE aid = :aid1;
END;
