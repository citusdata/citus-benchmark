\set scale 10000
\set aid1 random(1, 100000 * :scale)
\set aid2 random(1, 100000 * :scale)
\set delta1 random(-5000, 5000)
\set delta2 random(-5000, 5000)
BEGIN;
UPDATE pgbench_accounts SET abalance = abalance + :delta1 WHERE aid = :aid1;
UPDATE pgbench_accounts SET abalance = abalance + :delta2 WHERE aid = :aid2;
END;
