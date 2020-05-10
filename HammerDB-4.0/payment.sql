CREATE OR REPLACE PROCEDURE PAYMENT (
p_w_id			IN INTEGER,
p_d_id			IN INTEGER,	
p_c_w_id		IN INTEGER,	
p_c_d_id		IN INTEGER,	
byname			IN INTEGER,
p_h_amount		IN NUMERIC,
p_c_credit              INOUT CHAR(2),
p_c_last		INOUT VARCHAR(16),
p_c_id			INOUT NUMERIC(5,0),
p_w_street_1            INOUT VARCHAR(20),
p_w_street_2            INOUT VARCHAR(20),
p_w_city                INOUT VARCHAR(20),
p_w_state               INOUT CHAR(2),
p_w_zip                 INOUT CHAR(9),
p_d_street_1            INOUT VARCHAR(20),
p_d_street_2            INOUT VARCHAR(20),
p_d_city                INOUT VARCHAR(20),
p_d_state               INOUT CHAR(2),
p_d_zip                 INOUT CHAR(9),
p_c_first               INOUT VARCHAR(16),
p_c_middle              INOUT CHAR(2),
p_c_street_1            INOUT VARCHAR(20),
p_c_street_2            INOUT VARCHAR(20),
p_c_city                INOUT VARCHAR(20),
p_c_state               INOUT CHAR(2),
p_c_zip                 INOUT CHAR(9),
p_c_phone               INOUT CHAR(16),
p_c_since		INOUT TIMESTAMP,
p_c_credit_lim          INOUT NUMERIC(12,2),
p_c_discount            INOUT NUMERIC(4,4),
p_c_balance             INOUT NUMERIC(12,2),
p_c_data                INOUT VARCHAR(500),
tstamp			IN TIMESTAMP)
AS $$
DECLARE
namecnt			INTEGER;
p_d_name		VARCHAR(11);
p_w_name		VARCHAR(11);
p_c_new_data		VARCHAR(500);
h_data			VARCHAR(30);
c_byname CURSOR FOR
SELECT c_first, c_middle, c_id,
c_street_1, c_street_2, c_city, c_state, c_zip,
c_phone, c_credit, c_credit_lim,
c_discount, c_balance, c_since
FROM customer
WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND c_last = p_c_last
ORDER BY c_first;
BEGIN
UPDATE warehouse SET w_ytd = w_ytd + p_h_amount
WHERE w_id = p_w_id;
SELECT w_street_1, w_street_2, w_city, w_state, w_zip, w_name
INTO p_w_street_1, p_w_street_2, p_w_city, p_w_state, p_w_zip, p_w_name
FROM warehouse
WHERE w_id = p_w_id;
UPDATE district SET d_ytd = d_ytd + p_h_amount
WHERE d_w_id = p_w_id AND d_id = p_d_id;
SELECT d_street_1, d_street_2, d_city, d_state, d_zip, d_name
INTO p_d_street_1, p_d_street_2, p_d_city, p_d_state, p_d_zip, p_d_name
FROM district
WHERE d_w_id = p_w_id AND d_id = p_d_id;
IF ( byname = 1 )
THEN
SELECT count(c_id) INTO namecnt
FROM customer
WHERE c_last = p_c_last AND c_d_id = p_c_d_id AND c_w_id = p_c_w_id;
OPEN c_byname;
IF ( MOD (namecnt, 2) = 1 )
THEN
namecnt := (namecnt + 1);
END IF;
FOR loop_counter IN 0 .. cast((namecnt/2) AS INTEGER)
LOOP
FETCH c_byname
INTO p_c_first, p_c_middle, p_c_id, p_c_street_1, p_c_street_2, p_c_city,
p_c_state, p_c_zip, p_c_phone, p_c_credit, p_c_credit_lim, p_c_discount, p_c_balance, p_c_since;
END LOOP;
CLOSE c_byname;
ELSE
SELECT c_first, c_middle, c_last,
c_street_1, c_street_2, c_city, c_state, c_zip,
c_phone, c_credit, c_credit_lim,
c_discount, c_balance, c_since
INTO p_c_first, p_c_middle, p_c_last,
p_c_street_1, p_c_street_2, p_c_city, p_c_state, p_c_zip,
p_c_phone, p_c_credit, p_c_credit_lim,
p_c_discount, p_c_balance, p_c_since
FROM customer
WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND c_id = p_c_id;
END IF;
p_c_balance := ( p_c_balance + p_h_amount );
IF p_c_credit = 'BC' 
THEN
 SELECT c_data INTO p_c_data
FROM customer
WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND c_id = p_c_id;
h_data := p_w_name || ' ' || p_d_name;
p_c_new_data := (p_c_id || ' ' || p_c_d_id || ' ' || p_c_w_id || ' ' || p_d_id || ' ' || p_w_id || ' ' || TO_CHAR(p_h_amount,'9999.99') || TO_CHAR(tstamp,'YYYYMMDDHH24MISS') || h_data);
p_c_new_data := substr(CONCAT(p_c_new_data,p_c_data),1,500-(LENGTH(p_c_new_data)));
UPDATE customer
SET c_balance = p_c_balance, c_data = p_c_new_data
WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND
c_id = p_c_id;
ELSE
UPDATE customer SET c_balance = p_c_balance
WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND
c_id = p_c_id;
END IF;
h_data := p_w_name || ' ' || p_d_name;
INSERT INTO history (h_c_d_id, h_c_w_id, h_c_id, h_d_id,
h_w_id, h_date, h_amount, h_data)
VALUES (p_c_d_id, p_c_w_id, p_c_id, p_d_id,
p_w_id, tstamp, p_h_amount, h_data);
EXCEPTION
WHEN serialization_failure OR deadlock_detected OR no_data_found
THEN ROLLBACK;
--Cannot commit before exception handler
COMMIT;
END; 
$$
LANGUAGE 'plpgsql';
