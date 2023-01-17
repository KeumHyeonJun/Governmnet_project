from impala.dbapi import connect
from impala.util import as_pandas
conn = connect(host = '172.31.101.61', port = 21050 , user = 'hive', password = 'hive')
cur = conn.cursor()
create_query ='select * from SVC.hanmec1_vw_inout_errlpr_list'
# run query on impala
cur.execute(create_query)
hanmec1 = as_pandas(cur)