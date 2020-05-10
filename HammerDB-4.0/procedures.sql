CREATE OR REPLACE PROCEDURE NEWORD (
no_w_id         IN INTEGER,
no_max_w_id     IN INTEGER,
no_d_id         IN INTEGER,
no_c_id         IN INTEGER,
no_o_ol_cnt     IN INTEGER,
no_c_discount   INOUT NUMERIC,
no_c_last       INOUT VARCHAR,
no_c_credit     INOUT VARCHAR,
no_d_tax        INOUT NUMERIC,
no_w_tax        INOUT NUMERIC,
no_d_next_o_id  INOUT INTEGER,
tstamp          IN TIMESTAMP )
AS $$
DECLARE
    no_s_quantity		NUMERIC;
    no_o_all_local		SMALLINT;
    rbk					SMALLINT;
    item_id_array 		INT[];
    supply_wid_array	SMALLINT[];
    quantity_array		SMALLINT[];
    order_line_array	SMALLINT[];
    stock_dist_array	CHAR(24)[];
    s_quantity_array	SMALLINT[];
    price_array			NUMERIC(5,2)[];
    amount_array		NUMERIC(5,2)[];
BEGIN
	no_o_all_local := 1;
	SELECT c_discount, c_last, c_credit, w_tax
	INTO no_c_discount, no_c_last, no_c_credit, no_w_tax
	FROM customer, warehouse
	WHERE warehouse.w_id = no_w_id AND customer.c_w_id = no_w_id AND customer.c_d_id = no_d_id AND customer.c_id = no_c_id;

	--#2.4.1.4
	rbk := round(DBMS_RANDOM(1,100));
	--#2.4.1.5
	FOR loop_counter IN 1 .. no_o_ol_cnt
	LOOP
		IF ((loop_counter = no_o_ol_cnt) AND (rbk = 1))
		THEN
			item_id_array[loop_counter] := 100001;
		ELSE
			item_id_array[loop_counter] := round(DBMS_RANDOM(1,100000));
		END IF;

		--#2.4.1.5.2
		IF ( round(DBMS_RANDOM(1,100)) > 1 )
		THEN
			supply_wid_array[loop_counter] := no_w_id;
		ELSE
			no_o_all_local := 0;
			supply_wid_array[loop_counter] := 1 + MOD(CAST (no_w_id + round(DBMS_RANDOM(0,no_max_w_id-1)) AS INT), no_max_w_id);
		END IF;

		--#2.4.1.5.3
		quantity_array[loop_counter] := round(DBMS_RANDOM(1,10));
		order_line_array[loop_counter] := loop_counter;
	END LOOP;

	UPDATE district SET d_next_o_id = d_next_o_id + 1 WHERE d_id = no_d_id AND d_w_id = no_w_id RETURNING d_next_o_id, d_tax INTO no_d_next_o_id, no_d_tax;

	INSERT INTO ORDERS (o_id, o_d_id, o_w_id, o_c_id, o_entry_d, o_ol_cnt, o_all_local) VALUES (no_d_next_o_id, no_d_id, no_w_id, no_c_id, current_timestamp, no_o_ol_cnt, no_o_all_local);
	INSERT INTO NEW_ORDER (no_o_id, no_d_id, no_w_id) VALUES (no_d_next_o_id, no_d_id, no_w_id);

	SELECT array_agg ( i_price )
	INTO price_array
	FROM UNNEST(item_id_array) item_id
	LEFT JOIN item ON i_id = item_id;

	IF no_d_id = 1
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_01 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 2
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_02 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 3
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_03 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 4
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_04 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 5
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_05 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 6
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_06 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 7
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_07 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 8
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_08 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 9
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_09 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	ELSIF no_d_id = 10
	THEN
		WITH stock_update AS (
	        UPDATE stock
    	       SET s_quantity = ( CASE WHEN s_quantity < (item_stock.quantity + 10) THEN s_quantity + 91 ELSE s_quantity END) - item_stock.quantity
			  FROM UNNEST(item_id_array, supply_wid_array, quantity_array, price_array)
				   AS item_stock (item_id, supply_wid, quantity, price)
			 WHERE stock.s_i_id = item_stock.item_id
			   AND stock.s_w_id = item_stock.supply_wid
			   AND stock.s_w_id = ANY(supply_wid_array)
			RETURNING stock.s_dist_10 as s_dist, stock.s_quantity, ( item_stock.quantity + item_stock.price * ( 1 + no_w_tax + no_d_tax ) * ( 1 - no_c_discount ) ) amount
    	)
		SELECT array_agg ( s_dist ), array_agg ( s_quantity ), array_agg ( amount )
		FROM stock_update
		INTO stock_dist_array, s_quantity_array, amount_array;
	END IF;

	INSERT INTO order_line (ol_o_id, ol_d_id, ol_w_id, ol_number, ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_dist_info)
	SELECT no_d_next_o_id,
		   no_d_id,
		   no_w_id,
		   data.line_number,
		   data.item_id,
		   data.supply_wid,
		   data.quantity,
		   data.amount,
		   data.stock_dist
	  FROM UNNEST(order_line_array,
				   item_id_array,
				   supply_wid_array,
				   quantity_array,
				   amount_array,
				   stock_dist_array)
		   AS data( line_number, item_id, supply_wid, quantity, amount, stock_dist);

	no_s_quantity := 0;
	FOR loop_counter IN 1 .. no_o_ol_cnt
	LOOP
		no_s_quantity := no_s_quantity + CAST( amount_array[loop_counter] AS NUMERIC);
	END LOOP;

    EXCEPTION
        WHEN serialization_failure OR deadlock_detected OR no_data_found
            THEN ROLLBACK;
END;
$$
LANGUAGE 'plpgsql';
CREATE OR REPLACE PROCEDURE DELIVERY (
d_w_id          IN INTEGER,
d_o_carrier_id  IN  INTEGER,
tstamp          IN TIMESTAMP )
AS $$
DECLARE
loop_counter	SMALLINT;
d_id_in_array	SMALLINT[] := ARRAY[1,2,3,4,5,6,7,8,9,10];
d_id_array		SMALLINT[];
o_id_array 		INT[];
c_id_array 		INT[];
order_count		SMALLINT;
sum_amounts     NUMERIC[];

customer_count INT;
BEGIN
	WITH new_order_delete AS (
		DELETE
		 FROM new_order as del_new_order
		USING UNNEST(d_id_in_array) AS d_ids
		WHERE no_d_id = d_ids
		  AND no_w_id = d_w_id
		  AND del_new_order.no_o_id = (select min (select_new_order.no_o_id)
						   from new_order as select_new_order
						  where no_d_id = d_ids
							and no_w_id = d_w_id)
		RETURNING del_new_order.no_o_id, del_new_order.no_d_id
		)
	SELECT array_agg(no_o_id), array_agg(no_d_id)
	  FROM new_order_delete
	  INTO o_id_array, d_id_array;

	UPDATE orders
	   SET o_carrier_id = d_o_carrier_id
	  FROM UNNEST(o_id_array, d_id_array) AS ids(o_id, d_id)
	 WHERE orders.o_id = ids.o_id
	   AND o_d_id = ids.d_id
	   AND o_w_id = d_w_id;

	WITH order_line_update AS (
        UPDATE order_line
           SET ol_delivery_d = current_timestamp
		  FROM UNNEST(o_id_array, d_id_array) AS ids(o_id, d_id)
		 WHERE ol_o_id = ids.o_id
           AND ol_d_id = ids.d_id
           AND ol_w_id = d_w_id
		RETURNING ol_d_id, ol_o_id, ol_amount
		)
	SELECT array_agg(ol_d_id), array_agg(c_id), array_agg(sum_amount)
	  FROM ( SELECT ol_d_id,
			       ( SELECT DISTINCT o_c_id FROM orders WHERE o_id = ol_o_id AND o_d_id = ol_d_id AND o_w_id = d_w_id) AS c_id,
			        sum(ol_amount) AS sum_amount
			   FROM order_line_update
			  GROUP BY ol_d_id, ol_o_id ) AS inner_sum
	  INTO d_id_array, c_id_array, sum_amounts;

	UPDATE customer
	   SET c_balance = COALESCE(c_balance,0) + ids_and_sums.sum_amounts
	  FROM UNNEST(d_id_array, c_id_array, sum_amounts) AS ids_and_sums(d_id, c_id, sum_amounts)
	 WHERE customer.c_id = ids_and_sums.c_id
	   AND c_d_id = ids_and_sums.d_id
	   AND c_w_id = d_w_id;

    EXCEPTION
		WHEN serialization_failure OR deadlock_detected OR no_data_found
	        THEN ROLLBACK;
END;
$$
LANGUAGE 'plpgsql';
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
name_count		SMALLINT;
p_d_name		VARCHAR(11);
p_w_name		VARCHAR(11);
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
	UPDATE warehouse
	   SET w_ytd = w_ytd + p_h_amount
	 WHERE w_id = p_w_id
	 RETURNING w_street_1, w_street_2, w_city, w_state, w_zip, w_name
	 INTO p_w_street_1, p_w_street_2, p_w_city, p_w_state, p_w_zip, p_w_name;

	UPDATE district
	   SET d_ytd = d_ytd + p_h_amount
	 WHERE d_w_id = p_w_id AND d_id = p_d_id
	 RETURNING d_street_1, d_street_2, d_city, d_state, d_zip, d_name
	 INTO p_d_street_1, p_d_street_2, p_d_city, p_d_state, p_d_zip, p_d_name;

	IF ( byname = 1 )
	THEN
		SELECT count(c_last) INTO name_count
		FROM customer
		WHERE c_last = p_c_last AND c_d_id = p_c_d_id AND c_w_id = p_c_w_id;
		OPEN c_byname;
		FOR loop_counter IN 1 .. cast( name_count/2 AS INT)
		LOOP
			FETCH c_byname
			INTO p_c_first, p_c_middle, p_c_id, p_c_street_1, p_c_street_2, p_c_city, p_c_state, p_c_zip, p_c_phone, p_c_credit, p_c_credit_lim, p_c_discount, p_c_balance, p_c_since;
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

    h_data := p_w_name || ' ' || p_d_name;

	IF p_c_credit = 'BC'
	THEN
		UPDATE customer
		   SET c_balance = p_c_balance - p_h_amount,
		       c_data = substr ((p_c_id || ' ' ||
                                 p_c_d_id || ' ' ||
                                 p_c_w_id || ' ' ||
                                 p_d_id || ' ' ||
                                 p_w_id || ' ' ||
                                 to_char (p_h_amount, '9999.99') || ' ' ||
                                 TO_CHAR(tstamp,'YYYYMMDDHH24MISS') || ' ' ||
                                 h_data || ' | ') || c_data, 1, 500)
		 WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND c_id = p_c_id
		RETURNING c_balance, c_data INTO p_c_balance, p_c_data;
	ELSE
		UPDATE customer
		   SET c_balance = p_c_balance - p_h_amount
		 WHERE c_w_id = p_c_w_id AND c_d_id = p_c_d_id AND c_id = p_c_id
		RETURNING c_balance, c_data INTO p_c_balance, p_c_data;
	END IF;

	INSERT INTO history (h_c_d_id, h_c_w_id, h_c_id, h_d_id,h_w_id, h_date, h_amount, h_data)
	VALUES (p_c_d_id, p_c_w_id, p_c_id, p_d_id,	p_w_id, tstamp, p_h_amount, h_data);

    EXCEPTION
		WHEN serialization_failure OR deadlock_detected OR no_data_found
			THEN ROLLBACK;
END;
$$
LANGUAGE 'plpgsql';
CREATE OR REPLACE PROCEDURE OSTAT (
    os_w_id			IN INTEGER,
    os_d_id			IN INTEGER,
    os_c_id			INOUT INTEGER,
    byname			IN INTEGER,
    os_c_last		INOUT VARCHAR,
    os_c_first		INOUT VARCHAR,
    os_c_middle		INOUT VARCHAR,
    os_c_balance	INOUT NUMERIC,
    os_o_id			INOUT INTEGER,
    os_entdate		INOUT TIMESTAMP,
    os_o_carrier_id	INOUT INTEGER,
    os_c_line		INOUT TEXT DEFAULT '')
AS $$
DECLARE
    out_os_c_id	    INTEGER;
    out_os_c_last	VARCHAR;
    os_ol		    RECORD;
    namecnt		    INTEGER;
    c_name CURSOR FOR
    SELECT c_balance, c_first, c_middle, c_id
      FROM customer
     WHERE c_last = os_c_last AND c_d_id = os_d_id AND c_w_id = os_w_id
    ORDER BY c_first;
BEGIN
    IF ( byname = 1 )
    THEN
        SELECT count(c_id) INTO namecnt
        FROM customer
        WHERE c_last = os_c_last AND c_d_id = os_d_id AND c_w_id = os_w_id;

        IF ( MOD (namecnt, 2) = 1 )
        THEN
            namecnt := (namecnt + 1);
        END IF;

        OPEN c_name;
        FOR loop_counter IN 0 .. cast((namecnt/2) AS INTEGER)
        LOOP
            FETCH c_name
            INTO os_c_balance, os_c_first, os_c_middle, os_c_id;
        END LOOP;
        CLOSE c_name;
    ELSE
        SELECT c_balance, c_first, c_middle, c_last
        INTO os_c_balance, os_c_first, os_c_middle, os_c_last
        FROM customer
        WHERE c_id = os_c_id AND c_d_id = os_d_id AND c_w_id = os_w_id;
    END IF;

    SELECT o_id, o_carrier_id, o_entry_d
      INTO os_o_id, os_o_carrier_id, os_entdate
      FROM (SELECT o_id, o_carrier_id, o_entry_d
              FROM orders where o_d_id = os_d_id AND o_w_id = os_w_id and o_c_id=os_c_id
            ORDER BY o_id DESC) AS SUBQUERY
    LIMIT 1;

    FOR os_ol IN
    SELECT ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_delivery_d, out_os_c_id, out_os_c_last, os_c_first, os_c_middle, os_c_balance, os_o_id, os_entdate, os_o_carrier_id
      FROM order_line
     WHERE ol_o_id = os_o_id AND ol_d_id = os_d_id AND ol_w_id = os_w_id
    LOOP
        os_c_line := os_c_line || ',' || os_ol.ol_i_id || ',' || os_ol.ol_supply_w_id || ',' || os_ol.ol_quantity || ',' || os_ol.ol_amount || ',' || os_ol.ol_delivery_d;
    END LOOP;
EXCEPTION
    WHEN serialization_failure OR deadlock_detected OR no_data_found
        THEN ROLLBACK;
END;
$$
LANGUAGE 'plpgsql';
CREATE OR REPLACE PROCEDURE SLEV (
st_w_id			IN INTEGER,
st_d_id			IN INTEGER,
threshold		IN INTEGER,
stock_count		INOUT INTEGER )
AS $$
BEGIN
	SELECT COUNT(DISTINCT (s_i_id)) INTO stock_count
	  FROM order_line, stock, district
	 WHERE ol_w_id = st_w_id
	   AND ol_d_id = st_d_id
	   AND d_w_id=st_w_id
	   AND d_id=st_d_id
	   AND (ol_o_id < d_next_o_id)
	   AND ol_o_id >= (d_next_o_id - 20)
	   AND s_w_id = st_w_id
	   AND s_i_id = ol_i_id
	   AND s_quantity < threshold;
END;
$$
LANGUAGE 'plpgsql';
CREATE OR REPLACE FUNCTION DBMS_RANDOM (INTEGER, INTEGER) RETURNS INTEGER AS $$
DECLARE
    start_int ALIAS FOR $1;
    end_int ALIAS FOR $2;
BEGIN
    RETURN trunc(random() * (end_int-start_int) + start_int);
END;
$$ LANGUAGE 'plpgsql' STRICT;
