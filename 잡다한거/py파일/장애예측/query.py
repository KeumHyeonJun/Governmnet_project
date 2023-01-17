from impala.dbapi import connect
from impala.util import as_pandas
import datetime
import config

# FSMA10
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSA10')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select job_nm, job_cd, job_jisi_dt, job_enddt, job_shm, job_ehm from SVC.gfms_fmsa10'
cur = conn.cursor()
cur.execute(create_query)
FMSA10 = as_pandas(cur)

# FSMA11
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSA11')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select job_cd, fac_cd from SVC.gfms_fmsa11'
cur = conn.cursor()
cur.execute(create_query)
FMSA11 = as_pandas(cur)

# FSMB07
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSB07')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select * from SVC.gfms_fmsb07'
cur = conn.cursor()
cur.execute(create_query)
FMSB07 = as_pandas(cur)

# FSMB03
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSB03')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select * from SVC.gfms_fmsb03'
cur = conn.cursor()
cur.execute(create_query)
FMSB03 = as_pandas(cur)

# FSMX01
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSX01')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select bd_cd, bd_nm from SVC.gfms_fmsx01'
cur = conn.cursor()
cur.execute(create_query)
FMSX01 = as_pandas(cur)

# FSMX04
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSX04')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select class_cd, class_nm, class_parent, class_level from SVC.gfms_fmsx04'
cur = conn.cursor()
cur.execute(create_query)
FMSX04 = as_pandas(cur)

# FSMX05
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSX05')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select fac_cd, fac_nm, class_cd, bd_cd, fl_cd, fac_instdt from SVC.gfms_fmsx05'
cur = conn.cursor()
cur.execute(create_query)
FMSX05 = as_pandas(cur)

# FSMB06
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSB06')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select * from SVC.gfms_fmsb06'
cur = conn.cursor()
cur.execute(create_query)
FMSB06 = as_pandas(cur)

# FSMB30
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - FMSB30')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select mat_cd, mat_nm, mat_type, inv_qty from SVC.gfms_fmsb30'
cur = conn.cursor()
cur.execute(create_query)
FMSB30 = as_pandas(cur)

