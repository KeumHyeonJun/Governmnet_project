import pandas as pd
import numpy as np
import datetime
from pathlib import Path
import warnings
import os
import dev_output
from impala.dbapi import connect
from impala.util import as_pandas
import config

warnings.filterwarnings(action='ignore')

print('!!!!!!!!!!!!!!! Start output.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
raw_data = str(path) + '/raw_data/'
data = str(path) + '/data/'
if not os.path.exists(str(path)+'/data/'):
    os.makedirs(str(path)+'/data/')
	
##############time 수정###############3
time= dev_output.date
year = int(time[:4])
month = int(time[4:6])
day = int(time[6:8])
max_time = datetime.datetime(year,month,day)

# 데이터 불러오기
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
#데이터 로드
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select * from SVC.gfms_fmsa10'
cur = conn.cursor()
cur.execute(create_query)
FMSA10 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsa11'
cur.execute(create_query)
FMSA11 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsb07'
cur.execute(create_query)
FMSB07 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsb03'
cur.execute(create_query)
FMSB03 = as_pandas(cur)


create_query ='select * from SVC.gfms_fmsx01_new'
cur.execute(create_query)
FMSX01 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsx04'
cur.execute(create_query)
FMSX04 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsx05'
cur.execute(create_query)
FMSX05 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsb06'
cur.execute(create_query)
FMSB06 = as_pandas(cur)

create_query ='select * from SVC.gfms_fmsb30'
FMSB30 = as_pandas(cur)

FMSX01 = FMSX01[['bd_cd','bd_nm']]

# FMSA10 = pd.read_excel(raw_data+'FMSA10_작업지시_결과.xlsx')
# FMSA11 = pd.read_excel(raw_data + 'FMSA11_작업장비이력.xlsx')
# FMSB07 = pd.read_excel(raw_data + 'FMSB07_자재출고.xlsx')
# FMSB03 = pd.read_excel(raw_data + 'FMSB03_자재마스터.xlsx')
# FMSX01 = pd.read_excel(raw_data+'FMSX01_건물정보.xlsx')
# FMSX04 = pd.read_excel(raw_data+'FMSX04_장비계층.xlsx')
# FMSX05 = pd.read_excel(raw_data+'FMSX05_장비마스터.xlsx',dtype={'class_cd':str})
# FMSB06 = pd.read_excel(raw_data+"FMSB06_자재입고.xlsx")
# FMSB30 = pd.read_excel(raw_data+"FMSB30_자재재고.xlsx")

mec = pd.read_excel(raw_data + '수행자재_완료.xlsx',sheet_name='기계')
tel = pd.read_excel(raw_data +'수행자재_완료.xlsx',sheet_name='통신')
prevent = pd.read_excel(raw_data +'수행자재_완료.xlsx',sheet_name='방재')
elevator = pd.read_excel(raw_data +'수행자재_완료.xlsx',sheet_name='승강기')
electric = pd.read_excel(raw_data +'수행자재_완료.xlsx',sheet_name='전기')


# FMSA10.to_csv(data+"FMSA10.csv",index=False,encoding="utf-8-sig")
# FMSA11.to_csv(data+"FMSA11.csv",index=False,encoding="utf-8-sig")
# FMSB07.to_csv(data+"FMSB07.csv",index=False,encoding="utf-8-sig")
# FMSX04.to_csv(data+"FMSX04.csv",index=False,encoding="utf-8-sig")
# FMSB03.to_csv(data+"FMSB03.csv",index=False,encoding="utf-8-sig")
# FMSB06.to_csv(data+"FMSB06.csv",index=False,encoding="utf-8-sig")
# FMSB30.to_csv(data+"FMSB30.csv",index=False,encoding="utf-8-sig")
# mec.to_csv(data+"mec_finish.csv",index=False,encoding="utf-8-sig")
# tel.to_csv(data+"tel_finish.csv",index=False,encoding="utf-8-sig")
# prevent.to_csv(data+"prevent_finish.csv",index=False,encoding="utf-8-sig")
# elevator.to_csv(data+"elevator_finish.csv",index=False,encoding="utf-8-sig")
# electric.to_csv(data+"electric_finish.csv",index=False,encoding="utf-8-sig")


print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Preprocessing Data (FMSX05)')
#장비마스터 테이블 변환
#장비마스터 와 장비계층을 join하여 장비별로 정확한 장비계층 확인
FMSX05[['class_nm_1','class_nm_2','class_nm_3','class_nm_4','class_cd_1','class_cd_2','class_cd_3','class_cd_4']] = 0
arr = np.array(FMSX05)
col_list = list(FMSX05.columns)


hier = FMSX04[['class_nm','class_level','class_cd','class_parent']]
hier = hier[hier['class_cd']!='ROOT']
hier = pd.DataFrame(hier)
arr_hier =  np.array(hier)



# 장비마스터의 계층 정보가 레벨 4인 경우
def level4(i):
    # 레벨4넣기
    # num  = 장비마스터의 계층 코드 , clo_list의 index를 통해 2차원 배열상에서 위치 찾기 가능
    num = arr[i,col_list.index('class_cd')]
    # idx = 장비계층 테이블의 특정 장비의 계층 위치
    idx = np.where(arr_hier[:,2] == num)
    # 레벨 4의 계층, 코드를 넣기
    arr[i,col_list.index('class_nm_4')] =arr_hier[idx,0][0,0]
    arr[i,col_list.index('class_cd_4')] =arr_hier[idx,2][0,0]

    # 레벨3 넣기
    # 레벨4 > 계층테이블에서 해당하는 값 찾기 > 해당하는 부모 계층(레벨3)찾기 > 레벨3 넣기
    num = arr[i,col_list.index('class_cd_4')]
    idx = np.where(arr_hier[:,2] == num)
    # num_parents = 장비계층 테이블의 특정 장비의 부모계층 값
    num_parents = arr_hier[idx,3][0,0]
    #idx_parents =  장비계층 테이블의 특정 장비의 부모계층 위치
    idx_parents = np.where(arr_hier[:,2] == num_parents)
    # 레벨 3 을 넣기
    arr[i,col_list.index('class_nm_3')] =arr_hier[idx_parents,0][0,0]
    arr[i,col_list.index('class_cd_3')] =arr_hier[idx_parents,2][0,0]

    #레벨2 넣기
    num = arr[i,col_list.index('class_cd_3')]
    idx = np.where(arr_hier[:,2] == num)
    num_parents = arr_hier[idx,3][0,0]
    idx_parents = np.where(arr_hier[:,2] == num_parents)
    arr[i,col_list.index('class_nm_2')] =arr_hier[idx_parents,0][0,0]
    arr[i,col_list.index('class_cd_2')] =arr_hier[idx_parents,2][0,0]

    #레벨1 넣기
    num = arr[i,col_list.index('class_cd_2')]
    idx = np.where(arr_hier[:,2] == num)
    num_parents = arr_hier[idx,3][0,0]
    idx_parents = np.where(arr_hier[:,2] == num_parents)
    arr[i,col_list.index('class_nm_1')] =arr_hier[idx_parents,0][0,0]
    arr[i,col_list.index('class_cd_1')] =arr_hier[idx_parents,2][0,0]

# 장비마스터의 계층 정보가 레벨3인경우
def level3(i):
    # 레벨3 넣기
    num = arr[i,col_list.index('class_cd')]
    idx = np.where(arr_hier[:,2] == num)
    arr[i,col_list.index('class_nm_3')] =arr_hier[idx,0][0,0]
    arr[i,col_list.index('class_cd_3')] =arr_hier[idx,2][0,0]

    # 레벨2 넣기
    num = arr[i,col_list.index('class_cd_3')]
    idx = np.where(arr_hier[:,2] == num)
    num_parents = arr_hier[idx,3][0,0]
    idx_parents = np.where(arr_hier[:,2] == num_parents)
    arr[i,col_list.index('class_nm_2')] =arr_hier[idx_parents,0][0,0]
    arr[i,col_list.index('class_cd_2')] =arr_hier[idx_parents,2][0,0]

    #레벨1 넣기
    num = arr[i,col_list.index('class_cd_2')]
    idx = np.where(arr_hier[:,2] == num)
    num_parents = arr_hier[idx,3][0,0]
    idx_parents = np.where(arr_hier[:,2] == num_parents)
    arr[i,col_list.index('class_nm_1')] =arr_hier[idx_parents,0][0,0]
    arr[i,col_list.index('class_cd_1')] =arr_hier[idx_parents,2][0,0]

# 장비마스터의 계층 정보가 레벨2인경우
def level2(i):
    # 레벨2 넣기
    num = arr[i,col_list.index('class_cd')]
    idx = np.where(arr_hier[:,2] == num)
    arr[i,col_list.index('class_nm_2')] =arr_hier[idx,0][0,0]
    arr[i,col_list.index('class_cd_2')] =arr_hier[idx,2][0,0]

    # 레벨2 넣기
    num = arr[i,col_list.index('class_cd_2')]
    idx = np.where(arr_hier[:,2] == num)
    num_parents = arr_hier[idx,3][0,0]
    idx_parents = np.where(arr_hier[:,2] == num_parents)
    arr[i,col_list.index('class_nm_1')] =arr_hier[idx_parents,0][0,0]
    arr[i,col_list.index('class_cd_1')] =arr_hier[idx_parents,2][0,0]

# 장비마스터의 계층 정보가 레벨1인경우
def level1(i):
    #레벨1 넣기
    num = arr[i,col_list.index('class_cd')]
    idx = np.where(arr_hier[:,2] == num)
    arr[i,col_list.index('class_nm_1')] =arr_hier[idx,0][0,0]
    arr[i,col_list.index('class_cd_1')] =arr_hier[idx,2][0,0]




for i in range(len(arr)):
    if len(arr[i,col_list.index('class_cd')]) == 8:
        level4(i)
    elif len(arr[i,col_list.index('class_cd')]) == 6:
        level3(i)
    elif len(arr[i,col_list.index('class_cd')]) == 4:
        level2(i)
    elif len(arr[i,col_list.index('class_cd')]) == 2:
        level1(i)
		


FMSX05= pd.DataFrame(arr)
FMSX05.columns = col_list

#FMSX05.to_csv(data+'FMSX05_ver2.csv', index=False, encoding='utf-8-sig')


######################3 생존분석 전처리##########################33
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Preprocessing Data (survival analysis)')

FMSX05.rename(columns={'class_nm_4':'jangbi_class_nm_4'},inplace = True)
FMSX05.rename(columns={'class_nm_3':'jangbi_class_nm_3'},inplace = True)
FMSX05.rename(columns={'class_nm_2':'jangbi_class_nm_2'},inplace = True)
FMSX05.rename(columns={'class_nm_1':'jangbi_class_nm_1'},inplace = True)
FMSX05 = pd.merge(FMSX01,FMSX05, on='bd_cd', how = 'right')

# 필요한 컬럼만 추출하기
fmsa10 =FMSA10[['job_cd','job_nm','job_jisi_dt','job_enddt','job_shm','job_ehm']]
fmsb03 = FMSB03[['mat_cd','mat_nm']]
fmsx05 = FMSX05[['bd_cd','bd_nm','fl_cd','fac_cd','fac_nm','jangbi_class_nm_1','jangbi_class_nm_2','jangbi_class_nm_3','jangbi_class_nm_4','fac_instdt']]

# FMSB03과 inner join하기 위해 mat_cd 형식 일치 시키기
FMSB07["mat_cd"] = FMSB07["mat_cd"].astype("str")
FMSB07["mat_cd"] = list(map(lambda x: x[:-3],FMSB07["mat_cd"].tolist()))
fmsb03["mat_cd"] = fmsb03["mat_cd"].astype("str")

# mat_cd 기준으로 join 후 필요한 컬럼 추출
jajae = pd.merge(FMSB07,fmsb03 ,on = 'mat_cd', how = 'inner')
jajae = jajae[['job_cd','outw_day','mat_cd','outw_qty','mat_nm_x']]


jangbi = pd.merge(FMSA11, fmsx05, how='inner', on='fac_cd')

jangbi_broken = pd.merge(fmsa10,jangbi, on='job_cd',how = 'inner')

jangbi_broken.drop(['job_cont','chg_sysdt','chg_emp_no'],axis=1,inplace=True)
jangbi_broken = jangbi_broken.dropna()

jangbi_broken['jajae_matching'] = jangbi_broken['job_cd']

arr_장비 = list(jangbi_broken['job_cd'])
arr_자재 = list(jajae['job_cd'])

#arr = 자재 매칭이 되지 않는 고장난 장비
arr = list(set(arr_장비)- set(arr_자재))

def function(x):
    if x in arr:
        return 0
    else:
         return 1

# function을 통해 자재매칭 여부를 0,1 로 표현
jangbi_broken['jajae_matching'] = jangbi_broken['jajae_matching'].apply(function)
df = pd.merge(jangbi_broken,jajae, on='job_cd',how = 'inner')

final = df[['job_cd','job_nm','job_jisi_dt','job_enddt','job_shm','job_ehm','fac_cd','fac_nm','fac_instdt','mat_cd','mat_nm_x',
           'jangbi_class_nm_1','jangbi_class_nm_2','jangbi_class_nm_3','jangbi_class_nm_4','jajae_matching','mat_nm_x']]


jangbi_broken = jangbi_broken.sort_values('job_jisi_dt')

## 기준일자는 오늘로 설정해야 함 > 작업장비이력
jangbi_broken['rf_day'] = max_time

# 시간을 타입 변환
jangbi_broken['fac_instdt'] = pd.to_datetime(jangbi_broken['fac_instdt'])
jangbi_broken['job_jisi_dt'] = pd.to_datetime(jangbi_broken['job_jisi_dt'])

# 장비 설치 ~ 작업 까지의 간격 계산
jangbi_broken['install_job'] = jangbi_broken['job_jisi_dt'] - jangbi_broken['fac_instdt']

def slicing(x):
    return x[:-4]
jangbi_broken['install_job'] = jangbi_broken['install_job'].astype(str)
jangbi_broken = jangbi_broken.dropna()
jangbi_broken['install_job'] = jangbi_broken['install_job'].apply(slicing)
jangbi_broken['install_job'] = jangbi_broken['install_job'].astype(int)


jangbi_broken['job_job'] = 0
# 모두 장애가 발생한 장비이므로 job_cnt = 1 로 세팅
jangbi_broken['job_cnt'] = 1
jangbi_broken = jangbi_broken.sort_values(['fac_cd','install_job'])


# 작업-작업 간격 만들기
for i in range(len(jangbi_broken)):
    if i == 0:
        # 젤 처음 오는 경우 > 장비별 가장 오래된 작업
        jangbi_broken['job_job'].iloc[i] = jangbi_broken['install_job'].iloc[i]
    else :
        now_data = jangbi_broken['fac_cd'].iloc[i]
        past_data = jangbi_broken['fac_cd'].iloc[i-1]
        # 한 장비가 이전에 장애가 발생했을 경우
        if now_data == past_data:
            jangbi_broken['job_job'].iloc[i] = jangbi_broken['install_job'].iloc[i] - jangbi_broken['install_job'].iloc[i-1]
            jangbi_broken['job_cnt'].iloc[i] = jangbi_broken['job_cnt'].iloc[i-1] +1
        # 장비가 이전에 장애가 발생하지 않았을 경우
        else :
            jangbi_broken['job_job'].iloc[i] = jangbi_broken['install_job'].iloc[i]

# 필요한 컬럼만 선별 후 합치기
analysis_data = pd.merge(fmsx05,jangbi_broken[['job_jisi_dt','fac_cd','install_job','job_job','job_cnt','job_cd','job_nm']], on ='fac_cd', how ='left')

analysis_data['fac_instdt'] = pd.to_datetime(analysis_data['fac_instdt'])
# 장비 설치일자가 오늘보다 후에 된 경우 (이상한 데이터) 제거
analysis_data = analysis_data[analysis_data['fac_instdt'] <= max_time]


analysis_data['max_time'] = max_time
analysis_data['max_time'] = pd.to_datetime(analysis_data['max_time'])
# 작업_작업 간격, 설치_작업간격이 존재하지 않는 경우(수리 이력이 없는경우) 99999로 매핑
analysis_data['job_job'] = analysis_data['job_job'].fillna(999999)
analysis_data['install_job'] = analysis_data['install_job'].fillna(999999)

analysis_data['time'] = 0

def time(df):
    x = df['job_job']
    if x == 999999:
        return int((df['max_time'] -  df['fac_instdt']).days)
    else :
        return int(x)

def time2(df):
    x = df['install_job']
    if x == 999999:
        return int( (df['max_time'] -  df['fac_instdt']).days )
    else :
        return int(x)

def time3(df):
    if df['status'] == 0 :
        return int((df['max_time'] -  df['fac_instdt']).days)
    else :
        return int((df['max_time'] -  df['job_jisi_dt']).days)


def status(df):
    if df['job_cnt'] == 0:
        return 0
    else :
        return 1
    
analysis_data['job_cnt'] = analysis_data['job_cnt'].fillna(0)
analysis_data['job_job'] = analysis_data.apply(time,axis=1)
analysis_data['install_job'] = analysis_data.apply(time2,axis=1)
analysis_data['status'] = analysis_data.apply(status,axis=1)
analysis_data['time'] =  analysis_data.apply(time3,axis=1)
analysis_data = analysis_data.fillna(0)


performance_range = pd.concat([mec,tel,prevent,elevator,electric])
input_data= pd.merge(performance_range,analysis_data, how = 'left',left_on=['Lv1','Lv2','Lv3','Lv4'],right_on=['jangbi_class_nm_1','jangbi_class_nm_2','jangbi_class_nm_3','jangbi_class_nm_4'])
input_data.drop(['jangbi_class_nm_1','jangbi_class_nm_2','jangbi_class_nm_3','jangbi_class_nm_4'],axis=1,inplace = True)
input_data['비고'] = input_data['비고'].fillna(0)
input_data = input_data[input_data['time']>=0]
input_data = input_data[input_data['install_job']>=0]
input_data = input_data[input_data['job_job']>=0]
input_data = input_data.dropna()

#input_data.to_csv(data +'생존분석.csv', index = False, encoding = 'utf-8-sig')

