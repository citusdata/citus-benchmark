SELECT create_distributed_table('customer', 'c_w_id');
SELECT create_distributed_table('district', 'd_w_id');
SELECT create_distributed_table('history', 'h_w_id');
SELECT create_distributed_table('warehouse', 'w_id');
SELECT create_distributed_table('stock', 's_w_id');
SELECT create_distributed_table('new_order', 'no_w_id');
SELECT create_distributed_table('orders', 'o_w_id');
SELECT create_distributed_table('order_line', 'ol_w_id');
SELECT create_reference_table('item');
