#!/usr/bin/python

import sys
import os
import random
import atexit
import signal
import subprocess

from os.path import expanduser
from threading import Thread
from time import sleep
import time 

ch_queries = [
    """
select   ol_number,
     sum(ol_quantity) as sum_qty,
     sum(ol_amount) as sum_amount,
     avg(ol_quantity) as avg_qty,
     avg(ol_amount) as avg_amount,
     count(*) as count_order
from     order_line
group by ol_number order by ol_number LIMIT 10;
    """,
"""
select      su_suppkey, su_name, n_name, i_id, i_name, su_address, su_phone, su_comment
from     item, supplier, stock, nation, region,
     (select s_i_id as m_i_id,
         min(s_quantity) as m_s_quantity
     from     stock, supplier, nation, region
     where     mod((s_w_id*s_i_id),10000)=su_suppkey
          and su_nationkey=n_nationkey
          and n_regionkey=r_regionkey
          and r_name like 'Europ%'
     group by s_i_id) m
where      i_id = s_i_id
     and mod((s_w_id * s_i_id), 10000) = su_suppkey
     and su_nationkey = n_nationkey
     and n_regionkey = r_regionkey
     and i_data like '%b'
     and r_name like 'Europ%'
     and i_id=m_i_id
     and s_quantity = m_s_quantity
order by n_name, su_name, i_id LIMIT 10;
""",
"""
select   ol_o_id, ol_w_id, ol_d_id,
     sum(ol_amount) as revenue, o_entry_d
from      customer, new_order, orders, order_line
where      c_state like 'A%'
     and c_id = o_c_id
     and c_w_id = o_w_id
     and c_d_id = o_d_id
     and no_w_id = o_w_id
     and no_d_id = o_d_id
     and no_o_id = o_id
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
group by ol_o_id, ol_w_id, ol_d_id, o_entry_d
order by revenue desc, o_entry_d LIMIT 10;
""",
"""
select    o_ol_cnt, count(*) as order_count
from    orders
    where exists (select *
            from order_line
            where o_id = ol_o_id
            and o_w_id = ol_w_id
            and o_d_id = ol_d_id
            and ol_delivery_d >= o_entry_d)
group    by o_ol_cnt
order    by o_ol_cnt LIMIT 10;
""",
"""
select    sum(ol_amount) as revenue
from order_line
where ol_quantity between 1 and 100000 LIMIT 10;
""",
"""
select     su_nationkey as supp_nation,
     substr(c_state,1,1) as cust_nation,
     extract(year from o_entry_d) as l_year,
     sum(ol_amount) as revenue
from     supplier, stock, order_line, orders, customer, nation n1, nation n2
where     ol_supply_w_id = s_w_id
     and ol_i_id = s_i_id
     and mod((s_w_id * s_i_id), 10000) = su_suppkey
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
     and c_id = o_c_id
     and c_w_id = o_w_id
     and c_d_id = o_d_id
     and su_nationkey = n1.n_nationkey
     and ascii(substr(c_state,1,1)) = n2.n_nationkey
     and (
        (n1.n_name = 'Germany' and n2.n_name = 'Cambodia')
         or
        (n1.n_name = 'Cambodia' and n2.n_name = 'Germany')
         )
group by su_nationkey, substr(c_state,1,1), extract(year from o_entry_d)
order by su_nationkey, cust_nation, l_year LIMIT 10;
""",
"""
select     extract(year from o_entry_d) as l_year,
     sum(case when n2.n_name = 'Germany' then ol_amount else 0 end) / sum(ol_amount) as mkt_share
from     item, supplier, stock, order_line, orders, customer, nation n1, nation n2, region
where     i_id = s_i_id
     and ol_i_id = s_i_id
     and ol_supply_w_id = s_w_id
     and mod((s_w_id * s_i_id),10000) = su_suppkey
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
     and c_id = o_c_id
     and c_w_id = o_w_id
     and c_d_id = o_d_id
     and n1.n_nationkey = ascii(substr(c_state,1,1))
     and n1.n_regionkey = r_regionkey
     and ol_i_id < 1000
     and r_name = 'Europe'
     and su_nationkey = n2.n_nationkey
     and i_data like '%b'
     and i_id = ol_i_id
group by extract(year from o_entry_d)
order by l_year LIMIT 10;
""",
"""
select     n_name, extract(year from o_entry_d) as l_year, sum(ol_amount) as sum_profit
from     item, stock, supplier, order_line, orders, nation
where     ol_i_id = s_i_id
     and ol_supply_w_id = s_w_id
     and mod((s_w_id * s_i_id), 10000) = su_suppkey
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
     and ol_i_id = i_id
     and su_nationkey = n_nationkey
     and i_data like '%BB'
group by n_name, extract(year from o_entry_d)
order by n_name, l_year desc LIMIT 10;
""",
"""
select     c_id, c_last, sum(ol_amount) as revenue, c_city, c_phone, n_name
from     customer, orders, order_line, nation
where     c_id = o_c_id
     and c_w_id = o_w_id
     and c_d_id = o_d_id
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
     and o_entry_d <= ol_delivery_d
     and n_nationkey = ascii(substr(c_state,1,1))
group by c_id, c_last, c_city, c_phone, n_name
order by revenue desc LIMIT 10;
""",
"""
select     s_i_id, sum(s_order_cnt) as ordercount
from     stock, supplier, nation
where     mod((s_w_id * s_i_id),10000) = su_suppkey
     and su_nationkey = n_nationkey
     and n_name = 'Germany'
group by s_i_id
having   sum(s_order_cnt) >
        (select sum(s_order_cnt) * .005
        from stock, supplier, nation
        where mod((s_w_id * s_i_id),10000) = su_suppkey
        and su_nationkey = n_nationkey
        and n_name = 'Germany')
order by ordercount desc LIMIT 10;
""",
"""
select     o_ol_cnt,
     sum(case when o_carrier_id = 1 or o_carrier_id = 2 then 1 else 0 end) as high_line_count,
     sum(case when o_carrier_id <> 1 and o_carrier_id <> 2 then 1 else 0 end) as low_line_count
from     orders, order_line
where     ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
     and o_entry_d <= ol_delivery_d
group by o_ol_cnt
order by o_ol_cnt LIMIT 10;
""",
"""
select     c_count, count(*) as custdist
from     (select c_id, count(o_id)
     from customer left outer join orders on (
        c_w_id = o_w_id
        and c_d_id = o_d_id
        and c_id = o_c_id
        and o_carrier_id > 8)
     group by c_id) as c_orders (c_id, c_count)
group by c_count
order by custdist desc, c_count desc LIMIT 10;
""",
"""
select    100.00 * sum(case when i_data like 'PR%' then ol_amount else 0 end) / (1+sum(ol_amount)) as promo_revenue
from order_line, item
where ol_i_id = i_id 
    LIMIT 10;
""",
"""
with     revenue (supplier_no, total_revenue) as (
     select mod((s_w_id * s_i_id),10000) as supplier_no,
        sum(ol_amount) as total_revenue
     from order_line, stock
        where ol_i_id = s_i_id and ol_supply_w_id = s_w_id
     group by mod((s_w_id * s_i_id),10000))
select     su_suppkey, su_name, su_address, su_phone, total_revenue
from     supplier, revenue
where     su_suppkey = supplier_no
     and total_revenue = (select max(total_revenue) from revenue)
order by su_suppkey LIMIT 10;
""",
"""
select     i_name,
     substr(i_data, 1, 3) as brand,
     i_price,
     count(distinct (mod((s_w_id * s_i_id),10000))) as supplier_cnt
from     stock, item
where     i_id = s_i_id
     and i_data not like 'zz%'
     and (mod((s_w_id * s_i_id),10000) not in
        (select su_suppkey
         from supplier
         where su_comment like '%bad%'))
group by i_name, substr(i_data, 1, 3), i_price
order by supplier_cnt desc LIMIT 10;
""",
"""
select    sum(ol_amount) / 2.0 as avg_yearly
from order_line, (select   i_id, avg(ol_quantity) as a
            from     item, order_line
            where    i_data like '%b'
                 and ol_i_id = i_id
            group by i_id) t
where ol_i_id = t.i_id
    and ol_quantity < t.a LIMIT 10;
""",
"""
select     c_last, c_id o_id, o_entry_d, o_ol_cnt, sum(ol_amount)
from     customer, orders, order_line
where     c_id = o_c_id
     and c_w_id = o_w_id
     and c_d_id = o_d_id
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_o_id = o_id
group by o_id, o_w_id, o_d_id, c_id, c_last, o_entry_d, o_ol_cnt
having     sum(ol_amount) > 200
order by sum(ol_amount) desc, o_entry_d LIMIT 10;
""",
"""
select    sum(ol_amount) as revenue
from order_line, item
where    (
      ol_i_id = i_id
          and i_data like '%a'
          and ol_quantity >= 1
          and ol_quantity <= 10
          and i_price between 1 and 400000
          and ol_w_id in (1,2,3)
    ) or (
      ol_i_id = i_id
      and i_data like '%b'
      and ol_quantity >= 1
      and ol_quantity <= 10
      and i_price between 1 and 400000
      and ol_w_id in (1,2,4)
    ) or (
      ol_i_id = i_id
      and i_data like '%c'
      and ol_quantity >= 1
      and ol_quantity <= 10
      and i_price between 1 and 400000
      and ol_w_id in (1,5,3)
    ) LIMIT 10;
""",
"""
select   su_name, su_address
from     supplier, nation
where    su_suppkey in
        (select  mod(s_i_id * s_w_id, 10000)
        from     stock, order_line
        where    s_i_id in
                (select i_id
                 from item
                 where i_data like 'co%')
             and ol_i_id=s_i_id
        group by s_i_id, s_w_id, s_quantity
        having   2*s_quantity > sum(ol_quantity))
     and su_nationkey = n_nationkey
     and n_name = 'Germany'
order by su_name LIMIT 10;
""",
"""
select     su_name, count(*) as numwait
from     supplier, order_line l1, orders, stock, nation
where     ol_o_id = o_id
     and ol_w_id = o_w_id
     and ol_d_id = o_d_id
     and ol_w_id = s_w_id
     and ol_i_id = s_i_id
     and mod((s_w_id * s_i_id),10000) = su_suppkey
     and l1.ol_delivery_d > o_entry_d
     and not exists (select *
             from order_line l2
             where  l2.ol_o_id = l1.ol_o_id
                and l2.ol_w_id = l1.ol_w_id
                and l2.ol_d_id = l1.ol_d_id
                and l2.ol_delivery_d > l1.ol_delivery_d)
     and su_nationkey = n_nationkey
     and n_name = 'Germany'
group by su_name
order by numwait desc, su_name LIMIT 10;
""",
"""
select     substr(c_state,1,1) as country,
     count(*) as numcust,
     sum(c_balance) as totacctbal
from     customer
where     substr(c_phone,1,1) in ('1','2','3','4','5','6','7')
     and c_balance > (select avg(c_BALANCE)
              from      customer
              where  c_balance > 0.00
                  and substr(c_phone,1,1) in ('1','2','3','4','5','6','7'))
     and not exists (select *
             from    orders
             where    o_c_id = c_id
                     and o_w_id = c_w_id
                    and o_d_id = c_d_id)
group by substr(c_state,1,1)
order by substr(c_state,1,1) LIMIT 10;
"""
]

sent_query_amount = 0
is_terminated = False


def save_pid_to_file():
    my_pid = str(os.getpid())
    print(my_pid)
    home = expanduser("~")

    f_pid = open(os.path.join(home, "ch.pid"), 'w')
    f_pid.write(my_pid)
    f_pid.close()

def start_ch_thread():
    global sent_query_amount
    global ch_queries
    global is_terminated

    size = len(ch_queries)

#     cur_index = random.randint(0, size-1)
    cur_index = 0
    while not is_terminated:
        return_code = send_query(ch_queries[cur_index])
        # if there was an error, we will retry the same query
        if return_code != 0:
             continue
        sent_query_amount += 1
        
        cur_index += 1
        cur_index %= size

def send_query(query):
    global coord_ip
    pg = ['psql', '-P', 'pager=off', '-v', 'ON_ERROR_STOP=1', '-h', coord_ip, '-c', query]
    return subprocess.call(pg)
    



def give_stats(sent_query_amount, time_lapsed_in_secs):
    stat = "sent {} operations in {} seconds\n".format(sent_query_amount, time_lapsed_in_secs)
    print(stat)

    f = open("results/ch_results.txt", "a")
    f.write(stat)
    f.close()

def get_curtime_in_seconds():
    return int(round(time.time()))


def terminate():
    global is_terminated
    global sent_query_amount
    global start_time_in_secs
    
    end_time_in_secs = get_curtime_in_seconds()

    give_stats(sent_query_amount, end_time_in_secs - start_time_in_secs)

    is_terminated = True

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    global is_terminated
    self.kill_now = True
    print("got a kill signal")
    terminate()

if __name__ == "__main__":

    thread_count = int(sys.argv[1])
    coord_ip = sys.argv[2]
    initial_sleep_in_mins=int(sys.argv[3])
    
    save_pid_to_file()
    jobs = []
    for i in range(0, thread_count):
        thread = Thread(target = start_ch_thread)
        jobs.append(thread)

    sleep(initial_sleep_in_mins * 60)

    start_time_in_secs = get_curtime_in_seconds()
    for j in jobs:
        j.start()
        
    killer = GracefulKiller()
    f = open("results/ch_logs.txt", "a")
    while not killer.kill_now:
        time.sleep(10)

        now = get_curtime_in_seconds()
        f.write("running ch benchmarks ... sent {} queries in {} seconds\n".format(sent_query_amount, now - start_time_in_secs))    
    f.close()
