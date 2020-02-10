
-- THESE SHOULD BE UNCOMMENTED IF STORED PRODECURES ARE FALSE IN CONFIGS

-- SELECT create_distributed_function('public.dbms_random (integer, integer)');
-- SELECT create_distributed_function('public.delivery (integer, integer)', '$1', colocate_with := 'warehouse');
-- SELECT create_distributed_function('public.neword ( integer, integer, integer, integer, integer, integer)', '$1', colocate_with := 'warehouse');
-- SELECT create_distributed_function('public.payment ( integer, integer, integer, integer, numeric, integer, numeric, character varying, character varying, numeric)', '$1', colocate_with := 'warehouse');
-- SELECT create_distributed_function('public.slev ( integer, integer, integer)', '$1', colocate_with := 'warehouse');
-- SELECT create_distributed_function('public.ostat ( integer, integer, integer, integer, character varying)', '$1', colocate_with := 'warehouse');


-- THESE SHOULD BE COMMENTED IF STORED PRODECURES ARE FALSE IN CONFIGS

SELECT create_distributed_function('public.payment(integer,  integer,  integer,  integer,  integer,  numeric,  character,  character varying,  numeric,  character varying,  character varying,  character varying,  character, character, character varying,  character varying,  character varying,  character,  character, character varying,  character,  character varying,  character varying,  character varying,  character, character,  character,  timestamp without time zone,  numeric,  numeric,  numeric, character varying, timestamp without time zone)', '$1', colocate_with:='warehouse');
SELECT create_distributed_function('public.neword( integer, integer,  integer,  integer, integer,  numeric,  character varying,  character varying,  numeric,  numeric,  integer, timestamp without time zone)', '$1', colocate_with:='warehouse');
SELECT create_distributed_function('dbms_random(int,int)');
SELECT create_distributed_function('public.ostat( integer,  integer,  integer, integer,  character varying,  character varying,  character varying, numeric,  integer,  timestamp without time zone,  integer, text)', '$1', colocate_with:='warehouse');
SELECT create_distributed_function('public.slev(integer, integer,  integer,  integer)', '$1', colocate_with:='warehouse');
SELECT create_distributed_function('DELIVERY (INTEGER, INTEGER, Timestamp without time zone)', '$1', colocate_with:='warehouse');
