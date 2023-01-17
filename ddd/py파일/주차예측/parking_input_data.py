import datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import warnings
import requests
import holidays
import copy
import json
import re
import os

import parking_output
from impala.dbapi import connect
from impala.util import as_pandas
import config

date = parking_output.date
year = int(date[:4])
month = int(date[4:6])
day = int(date[6:])

warnings.filterwarnings(action='ignore')

print('!!!!!!!!!!!!!!! Start output.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

path = Path.cwd().parent
raw_data = str(path) + '/raw_data/'
data = str(path) + '/data/'
if not os.path.exists(str(path)+'/data/'):
    os.makedirs(str(path)+'/data/')

#### 향후 수정사항
def slicing(df,i) :
    pattern = '.*동'
    reg = re.search(pattern, df['장비명'][i])
    reg = reg.group()
    df['주차장'][i] = reg
    return reg
def change(x):
    if x =='13-1동' or x =='13-2동' or x =='13-3동':
        return '13동'
    elif x == '14-1동' or x == '14-2동':
        return '14동'
    else :
        return x


def parking(x):
    if x == '주차1동':
        return 101
    elif x == '주차2동':
        return 102
    else :
        for park in range(1,18):
            if x ==f'{park}동':
                return park



def confusion(df):
    if df['비율'] <= 0.3:
        return 0
    elif df['비율'] <= 0.5:
        return 1
    elif df['비율'] <= 0.8:
        return 2
    else:
        return 3

satsun = ['Independence Movement Day','Liberation Day','National Foundation Day','Hangeul Day',"Children's Day"]
kr_holidays = holidays.KR()
def holiday_check(date):
    if date in kr_holidays:
        return 1
    elif date.weekday() == 0:
        if (kr_holidays.get(datetime.datetime.strftime(date-relativedelta(days=1),"%Y-%m-%d")) or kr_holidays.get(datetime.datetime.strftime(date-relativedelta(days=2),"%Y-%m-%d"))) in satsun:
            return 1
        else:
            return 0
    else:
        return 0


def minute_yn(df):
    num = int(60/time_delta)
    for i in range(num):
        if df['분'] <= time_delta*i + time_delta-1 :
            return i




def replace_rain(df):
    if df['강수량(mm)'] == '1.0mm미만':
        return 0.5
    elif df['강수량(mm)'] == '30.0~50.0mm':
        return 40
    elif df['강수량(mm)'] == '50.0mm이상':
        return 60
    else:
        return float(str(df['강수량(mm)']).replace('mm', ''))


def replace_snow(df):
    if df['적설(cm)'] == '1cm미만':
        return 0.5
    elif df['적설(cm)'] == '5cm이상':
        return 5
    else:
        return float(str(df['적설(cm)']).replace('cm', ''))

first_pred_time = 7
# 예측종료시간
finish_pred_time = 10
#예측시간간격
time_delta = 30
# conn = connect(host = '172.31.101.61', port = 21050 , user = 'hive', password = 'hive')
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
print('connect')

#### 데이터 로드
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
parking_info = pd.read_excel(raw_data+'주차장면수.xlsx')

#날씨데이터 불러오기


create_query ='select * from SVC.ext_kma_asos_hourly_info_nopartition'
cur = conn.cursor()
cur.execute(create_query)
whether_his = as_pandas(cur)

create_query ='select * from SVC.ext_kma_vilage_fcst_nopartition'
cur = conn.cursor()
cur.execute(create_query)
whether_pre = as_pandas(cur)
cur.close()
print('Whether load')

# 예보데이터
conn = connect(host = '172.31.101.61', port = 21050 , user = 'hive', password = 'hive')
create_query ='select * from SVC.ext_kma_asos_hourly_info'
# run query on impala
cur = conn.cursor()
cur.execute(create_query)
whether_his = as_pandas(cur)
whether_his = whether_his.sort_values(by='tm')

create_query ='select * from SVC.ext_kma_vilage_fcst'
# run query on impala
cur = conn.cursor()
cur.execute(create_query)
whether_pre = as_pandas(cur)
cur.close()

# 예보데이터
df_tmp = whether_pre[whether_pre["category"]=="TMP"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"기온(°C)"})
df_pcp = whether_pre[whether_pre["category"]=="PCP"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"강수량(mm)"})
df_wsd = whether_pre[whether_pre["category"]=="WSD"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"풍속(m/s)"})
df_reh = whether_pre[whether_pre["category"]=="REH"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"습도(%)"})
df_sno = whether_pre[whether_pre["category"]=="SNO"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"적설(cm)"})

df_pcp.loc[df_pcp["강수량(mm)"]=="강수없음","강수량(mm)"] = 0
df_sno.loc[df_sno["적설(cm)"]=="적설없음","적설(cm)"] = 0

final_df = df_tmp.copy()
final_df = pd.merge(final_df,df_pcp,on=["일시","시간"],how="left")
final_df = pd.merge(final_df,df_wsd,on=["일시","시간"],how="left")
final_df = pd.merge(final_df,df_reh,on=["일시","시간"],how="left")
final_df = pd.merge(final_df,df_sno,on=["일시","시간"],how="left")

def converttime(x):
    return str('000000'+str(x))[-4:]

def convertday(x):
    y = x[:4]
    m = x[4:6]
    d = x[6:8]
    h = x[8:10]
    min = x[10:12]
    return y+'-'+m+'-'+d+' '+h+':'+min
final_df['시간'] = final_df['시간'].apply(converttime)

final_df['일시'] = final_df['일시'] + final_df['시간']

final_df['일시'] = final_df['일시'].apply(convertday)
final_df['일시'] = pd.to_datetime(final_df['일시'])

whether_pre = final_df.drop("시간",axis=1)
whether_pre['적설(cm)'] = whether_pre.apply(replace_snow,axis=1)
whether_pre['강수량(mm)'] = whether_pre.apply(replace_rain,axis=1)
#과거데이터
whether_his = whether_his[['tm','ta','rn','ws','hm','dsnw']]
whether_his.replace('',0,inplace=True)

whether_his.columns = whether_pre.columns


whether_his['일시'] = pd.to_datetime(whether_his['일시'])
whether_pre['일시'] = pd.to_datetime(whether_pre['일시'])

#차량데이터 불러오기
print('car load')
create_query ='select * from SVC.hanmec1_vw_inout_errlpr_list'
cur = conn.cursor()
cur.execute(create_query)
hanmec1 = as_pandas(cur)

create_query ='select * from SVC.hanmec2_vw_inout_errlpr_list'
cur = conn.cursor()
cur.execute(create_query)
hanmec2 = as_pandas(cur)

print('hanmec load')

create_query ='select * from SVC.daewoong_ps070'
cur = conn.cursor()
cur.execute(create_query)
daewoong_ps070 = as_pandas(cur)

create_query ='select * from SVC.daewoong_ps500'
cur = conn.cursor()
cur.execute(create_query)
daewoong_in = as_pandas(cur)

create_query ='select * from SVC.daewoong_ps510'
cur = conn.cursor()
cur.execute(create_query)
daewoong_out = as_pandas(cur)
print('daewoong load')

create_query ='select * from SVC.dklee_tb_pch302'
cur = conn.cursor()
cur.execute(create_query)
dklee = as_pandas(cur)


create_query ='select * from SVC.dklee_tb_pcn211'
cur = conn.cursor()
cur.execute(create_query)
dklee_tb_pcn211 = as_pandas(cur)
print('dk load')

# 한맥 전처리
hanmec1 = hanmec1[['carno','carinoutdtime','inoutdiv']]
hanmec2 = hanmec2[['carno','carinoutdtime','inoutdiv']]
hanmec1['주차장'] = '주차1동'
hanmec2['주차장'] = '주차2동'
hanmmec = pd.concat([hanmec1,hanmec2])
hanmmec = hanmmec[['carno','주차장','inoutdiv','carinoutdtime']]
hanmmec.columns = ['차량번호','주차장','입출차여부','입출차시각']
hanmmec['입출차여부'] = hanmmec['입출차여부'].apply(lambda x : '입차' if x ==1 else '출차')

# 대웅전처리
# daewoong_ps070 = pd.read_csv('daewoong_ps070.csv')
# daewoong_in = pd.read_csv('daewoong_in.csv')
# daewoong_out = pd.read_csv('daewoong_out.csv')




daewoong_in['입출차여부'] = '입차'
daewoong_out['입출차여부'] = '출차'
daewoong_out = daewoong_out[['outcarno','exitmainunitno','입출차여부','insdate']]
daewoong_in = daewoong_in[['incarno','mainunitno','입출차여부','insdate']]
daewoong_out.columns = ['차량번호', '주차장', '입출차여부','입출차시각']
daewoong_in.columns = ['차량번호', '주차장', '입출차여부','입출차시각']
daewoong = pd.concat([daewoong_in,daewoong_out])

daewoong = pd.merge(daewoong,daewoong_ps070[['mainunitno','unitname']], how = 'left', left_on='주차장',right_on='mainunitno')
daewoong = daewoong[['차량번호','unitname','입출차여부','입출차시각']]
daewoong.columns = ['차량번호', '주차장', '입출차여부','입출차시각']
daewoong['입출차시각'] = pd.to_datetime(daewoong['입출차시각'])

#차량번호 미인식 삭제
daewoong = daewoong[daewoong['차량번호']!='xxxxxxx']

def daewoong_parking(df):
    if 'A' in str(df):
        return '16동'
    elif 'B' in str(df):
        return '17동'
daewoong['주차장'] = daewoong['주차장'].apply(daewoong_parking)

#대경전처리

pd.set_option('display.max_columns', None)


dklee_in=dklee[['car_entr_eqp_no','car_entr_proc_ymd','car_entr_proc_time','car_entr_car_no']]
dklee_in['입출차여부'] = '입차'
dklee_out = dklee[['car_exit_eqp_no', 'car_exit_proc_ymd', 'car_exit_proc_time', 'car_exit_car_no']]
dklee_out['입출차여부'] = '출차'
dklee_out.columns =['장비코드','연월일','시간','차량번호','입출차여부']
dklee_in.columns =['장비코드','연월일','시간','차량번호','입출차여부']
dklee_in = dklee_in.dropna()
dklee_out = dklee_out.dropna()


#--------------------------------------------------------------------------------------------------------------------
# 이부분은 csv로 불러올때만 필요함!
# dklee_in[['장비코드','연월일','시간']] = dklee_in[['장비코드','연월일','시간']].astype(int).astype(str)
# dklee_out[['장비코드','연월일','시간']] = dklee_out[['장비코드','연월일','시간']].astype(int).astype(str)
#
# def replace(x):
#     return str('00000000000'+str(x))[-6:]
# dklee_out['시간'] = dklee_out['시간'].apply(replace)
# dklee_in['시간'] = dklee_in['시간'].apply(replace)
##########-------------------------------------------------------------------------------------

dk = pd.concat([dklee_in,dklee_out])
dk = dk.astype(str)


dk = pd.merge(dk, dklee_tb_pcn211[['eqp_no','eqp_nm']].astype(str), how = 'left', left_on='장비코드', right_on='eqp_no')
dk.rename(columns ={'eqp_nm':'장비명'},inplace = True)
dk.dropna(inplace = True)



def dk_parking(df):
    if '2동' in df:
        return '2동'
    elif '4동' in df:
        return '4동'
    elif '5동' in df:
        return '5동'
    elif '6동' in df:
        return '6동'
    else :
        return '7동'
dk['주차장']=dk['장비명'].apply(dk_parking)
dk['입출차시각'] = dk['연월일']+dk['시간']
dk['입출차시각'] = pd.to_datetime(dk['입출차시각'], format='%Y%m%d%H%M%S')
dk = dk[['차량번호','주차장','입출차여부','입출차시각']]

#다래전처리


# #### 전처리
# print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Preprocessing Data')
# # 공백 제거
# darae_in[['장비명','입차구분','입차고객구분','출차여부','차량종류']] = darae_in[['장비명','입차구분','입차고객구분','출차여부','차량종류']].apply(lambda x: x.str.strip())
# darae_out[['장비명','출차구분','출차고객구분','출차여부','차량종류']] = darae_out[['장비명','출차구분','출차고객구분','출차여부','차량종류']].apply(lambda x: x.str.strip())
#
#
# # 장비명에서 동만 추출하여 주차장에 입력
# darae_in['주차장'] = 0
# for i in range(len(darae_in)):
#     slicing(darae_in,i)
# darae_out['주차장'] = 0
# for i in range(len(darae_out)):
#     slicing(darae_out,i)
#
# # 13-1, 2, 3, 14-1, 2동을 13동, 14동으로 변경
# # darae_in['주차장'] = darae_in['주차장'].apply(change)
# # darae_out['주차장'] = darae_out['주차장'].apply(change)
# test_in = copy.deepcopy(darae_in)
# test_in.columns = ['일자','시각','차량번호','주차일련번호','입출차카드번호','장비명','입출차구분','입출차고객구분','출차여부','차량종류','주차장']
# test_in['입출차여부'] = '입차'
# test_out = copy.deepcopy(darae_out)
# test_out.columns = ['일자','시각','차량번호','주차일련번호','입출차카드번호','장비명','입출차구분','입출차고객구분','출차여부','차량종류','주차장']
# test_out['입출차여부'] = '출차'
#
# test_in['입출차시각'] = test_in['일자'] + test_in['시각']
# test_in['입출차시각'] = pd.to_datetime(test_in['입출차시각'], format= '%Y-%m-%d %H:%M:%S', errors='raise')
#
# test_out['입출차시각'] = test_out['일자'] + test_out['시각']
# test_out['입출차시각'] = pd.to_datetime(test_out['입출차시각'], format= '%Y-%m-%d %H:%M:%S', errors='raise')
#
# test_out = test_out[['차량번호','주차장','입출차여부','입출차시각']]
# test_in = test_in[['차량번호','주차장','입출차여부','입출차시각']]
# darae = pd.concat([test_in, test_out])

#병합 및 데이터셋 구축

# 입차, 출차 데이터 합치고 시간으로 정렬
df = pd.concat([hanmmec,daewoong,dk]).sort_values(by=['차량번호','입출차시각'])

df['입출차시각'] = pd.to_datetime(df['입출차시각'])
df['주차장'] = df['주차장'].apply(change)
# import datetime ############ import는 맨 위로 빼둠
# 입출차시각 생성
df['시'] = df['입출차시각'].dt.hour
# df.reset_index(inplace = True)
df.reset_index(inplace=True, drop=True) ######### 어차피 밑에서 index 삭제함 --> reset_index할 때 drop
df=df[['차량번호','주차장','입출차여부','입출차시각']]

car_arr = np.array(df[['입출차시각','차량번호']])
test_idx_list =[]

# 입차 시간과 출차시간이 같은 경우를 test_idx_list에 추가
for idx in range(len(car_arr)-1):
    # if car_arr[idx][0] == car_arr[idx+1][0] and car_arr[idx][1] == car_arr[idx+1][1] and car_arr[idx][2] == car_arr[idx+1][2]:
    if (car_arr[idx][0] == car_arr[idx+1][0]) and (car_arr[idx][1] == car_arr[idx+1][1]): ###### 가독성을 위해 조건에 괄호 쳐줌
        test_idx_list.append(idx)
        test_idx_list.append(idx+1)
test_idx_list = list(set(test_idx_list))
test_df = df.loc[test_idx_list]
# 입출차 시간이 같은 경우의 출차 삭제
eleminate_index = test_df[test_df['입출차여부']=='출차'].index
df2 = df.drop(eleminate_index).reset_index(drop=True) ############### 위에서 drop해서 index 컬럼 사라짐, 밑에 있는 reset_index를 위에 붙이고 index를 한번에 drop
# df2.drop(['index'],axis = 1 , inplace = True)
# df2.reset_index(inplace=True)
# df2.drop(['index'],axis = 1 , inplace = True)


# 아래 주석의 두 경우만 남김
car_arr = np.array(df2[['차량번호','입출차여부']])
idx_list = []
for idx in range(len(car_arr)):
    if idx == 0:
        idx_list.append(idx)
    else:
        # 차량 번호가 같고 상태가 다른 경우(입차 > 출차 or 출차 > 입차)
        if (car_arr[idx][0] == car_arr[idx-1][0]) and (car_arr[idx][1] != car_arr[idx-1][1]):
            idx_list.append(idx)
        #차량번호가 바뀌는 경우
        elif car_arr[idx][0] != car_arr[idx-1][0]:
            idx_list.append(idx)
process_df = df2.loc[idx_list]

# 연, 월, 일, 시, 분, 초 컬럼 생성
process_df['연'] = process_df['입출차시각'].dt.year
process_df['월'] = process_df['입출차시각'].dt.month
process_df['일'] = process_df['입출차시각'].dt.day
process_df['시'] = process_df['입출차시각'].dt.hour
process_df['분'] = process_df['입출차시각'].dt.minute
process_df['초'] = process_df['입출차시각'].dt.second
# 출근시간 (7시~9시) 사이만 남김
process_df = process_df[(process_df['시']>=first_pred_time) & (process_df['시']<=finish_pred_time-1)]

# 주차장 면수와 합치고 필요한 컬럼만 남김
# !!!!!!!!!!!!!!!!!! 13-1동옥외, 13-2동옥외 등은 고려하지 않는 건지? (따로 정리해뒀다가 데이터 붙일 때 현업한테 얘기해야할듯)
dataset = pd.merge(process_df, parking_info[['장소','합계']], left_on='주차장', right_on='장소')
dataset = dataset[['입출차시각','연','월','일','시','분','초','입출차여부','주차장','합계']]
dataset = dataset.sort_values(by=['주차장','입출차시각'])
dataset['잔류차량수'] = 0
arr = np.array(dataset[['연','월','일','시','분','입출차여부','주차장','잔류차량수']])

# 잔류차량수 생성
for idx in range(len(arr)):
    if idx == 0:
        # 첫번째 행이 입차이면 1, 출차이면 -1
        if arr[idx][5]=='입차':
            arr[idx][7] = arr[idx][7] + 1
        else:
            arr[idx][7] = arr[idx][7] - 1
    else:
        pre_time = list(arr[idx-1][[0,1,2,6]])
        now_time = list(arr[idx][[0,1,2,6]])
        status =  arr[idx][5]
        # 이전 데이터와 연,월,일 주차장이 같은 경우
        if pre_time == now_time:
            if status == '입차':
                arr[idx][7] = arr[idx-1][7] + 1
            else:
                arr[idx][7] = arr[idx-1][7] - 1
        #이전 데이터와 연,월,일 주차장이 다른 경우 > 0부터 시작함
        else:
            if status == '입차':
                arr[idx][7] = 1
            else:
                arr[idx][7] = -1
# 사용 데이터 정리 및 비율, 혼잡도 산출
dataset[['연','월','일','시','분','입출차여부','주차장','잔류차량수']] = arr
dataset['비율'] = dataset['잔류차량수'] / dataset['합계']
dataset['혼잡도'] = dataset.apply(confusion,axis=1)
dataset['공휴일'] = dataset['입출차시각'].apply(holiday_check)
dataset['요일'] = dataset['입출차시각'].dt.weekday
dataset = dataset[['입출차시각', '연', '월', '일', '시', '분','초','공휴일','요일','주차장','잔류차량수', '비율','혼잡도']]
# 날짜 매칭이 안되는 데이터들 제거
dataset = dataset.dropna()
dataset['주차장'] = dataset['주차장'].apply(parking)
# 불필요한 컬럼 제거
# dataset.drop('입출차시각', axis=1, inplace= True)
# dataset.drop('초', axis=1, inplace= True) #################### 여러 컬럼을 한번에 제거하면 됨. 잔류차량수와 비율 컬럼도 사용하지 않으므로 제거
dataset.drop(['입출차시각', '초', '잔류차량수', '비율'], axis=1, inplace=True)

# 날씨데이터 붙이기
## 학습데이터셋 생성
whether_his['일시'] = pd.to_datetime(whether_his['일시'])
whether_pre['일시'] = pd.to_datetime(whether_pre['일시'])

# 연, 월, 일, 시 생성
whether_his['연'] = whether_his['일시'].dt.year
whether_his['월'] = whether_his['일시'].dt.month
whether_his['일'] = whether_his['일시'].dt.day
whether_his['시'] = whether_his['일시'].dt.hour
# 위에서 만든 데이터셋에 날씨 데이터 붙여줌
dataset = pd.merge(dataset, whether_his, on=['연','월','일','시'], how='left')

# import holidays ######### import는 맨 위로 뺌
# 휴일 체크


# 날짜 매칭이 안되는 데이터들 제거
dataset = dataset.dropna()
# 불필요한 컬럼 제거
# dataset.drop('입출차시각', axis=1, inplace= True)
# dataset.drop('초', axis=1, inplace= True) #################### 여러 컬럼을 한번에 제거하면 됨. 잔류차량수와 비율 컬럼도 사용하지 않으므로 제

# dataset['tmp'] = dataset.apply(tmp, axis =1)
dataset['minute_yn'] = dataset.apply(minute_yn, axis =1) ############ 컬럼명 tmp에서 minute_yn으로 변경
dataframe = dataset.groupby(['연','월','일','시','minute_yn']).count().reset_index()[['연','월','일','시','minute_yn']]
dataframe['trend'] = range(0, len(dataframe))
dataset = pd.merge(dataset, dataframe, on=['연','월','일','시','minute_yn'], how='left')
dataset.drop('minute_yn', axis=1, inplace=True)

# dataset.index = dataset['trend']
# dataset.drop('trend', axis=1, inplace=True)
dataset.set_index('trend', inplace=True) ################# index설정 후 drop 대신 set_index 활용
dataset.reset_index(inplace=True)

# 최근 3년의 데이터만 사용
time  = pd.to_datetime(datetime.date(year, month, day) - datetime.timedelta(days=1095))
dataset['일시'] = pd.to_datetime(dataset['일시']).dt.date
dataset = dataset[dataset['일시']>=time]

dataset.drop('일시',inplace = True,axis=1)


#예측데이터 생성

print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Make Predict Data')

year = int(date[:4])
month = int(date[4:6])
day = int(date[6:])

len_df = (finish_pred_time -first_pred_time) * 60/time_delta +1

time = datetime.datetime(year, month, day,first_pred_time,0)
delta = datetime.timedelta(days=0, minutes=time_delta)
day_delta = datetime.timedelta(days=2, hours = finish_pred_time - first_pred_time)
time_list = [time]


while time < datetime.datetime(year, month, day,first_pred_time,0)+ day_delta:
    time = time + delta
    time_list.append(time)

time_df = pd.DataFrame(time_list)

time_df['연'] = time_df[0].dt.year
time_df['월'] = time_df[0].dt.month
time_df['일'] = time_df[0].dt.day
time_df['시'] = time_df[0].dt.hour
time_df['분'] = time_df[0].dt.minute
time_df2 = time_df[(time_df['시']== finish_pred_time) & (time_df['분']==0)]
time_df = time_df[(time_df['시']>= first_pred_time) & (time_df['시']<= finish_pred_time-1)]
time_df = pd.concat([time_df,time_df2])
time_df = time_df.sort_values(['연','월','일','시','분'])

whether_pre['연'] = whether_pre['일시'].dt.year
whether_pre['월'] = whether_pre['일시'].dt.month
whether_pre['일'] = whether_pre['일시'].dt.day
whether_pre['시'] = whether_pre['일시'].dt.hour


parking_list = dataset['주차장'].unique()

predict_dataset=  pd.DataFrame()
for parking in parking_list:
    predict_df = time_df
    predict_df['주차장']=parking
    predict_df = predict_df.sort_values(by=['일','시','분'])
    predict_df['공휴일'] = predict_df[0].apply(holiday_check)
    predict_df['요일'] = predict_df[0].dt.weekday
    predict_df['trend'] = range(dataset['trend'].max()+1, dataset['trend'].max() +1+ len(predict_df) )
    predict_dataset = pd.concat([predict_dataset,predict_df])
predict_dataset.drop(0,axis =1,inplace= True)


predict_dataset = pd.merge(predict_dataset,whether_pre, how = 'left', on = ['연','월','일','시'])
predict_dataset = predict_dataset.drop(['일시'],axis =1)
predict_dataset = predict_dataset.rename(columns = {'분_x':'분'})

# nan값이 있는경우  즉, 예보가 업데이트가 되지 않은 경우 작년 날짜를 가져와서 합친다
if predict_dataset.isnull().sum().max() >=1:
    print(f'예보데이터가 없는 경우가 {predict_dataset.isnull().sum().max()} 개 존재합니다')
    null_data = predict_dataset[predict_dataset['기온(°C)'].isnull()].iloc[:,:9]
    null_data = pd.merge(null_data,whether_his, how = 'left',on =['월','일','시'])
    def yearcompare(df):
        if abs(df['연_x'] - df['연_y']) ==1:
            return 1
        else :
            return 0
    null_data['compare'] = null_data.apply(yearcompare,axis =1)
    null_data =null_data[null_data['compare']==1]
    null_data = null_data[['trend', '연_x', '월', '일', '시', '분', '공휴일', '요일', '주차장', '기온(°C)',
           '강수량(mm)', '풍속(m/s)', '습도(%)', '적설(cm)']]
    null_data.rename(columns={'연_x':'연'},inplace = True)

    not_null = predict_dataset[predict_dataset['기온(°C)'].isnull() == False]
    predict_dataset = pd.concat([null_data,not_null])

    predict_dataset = pd.merge(predict_dataset,whether_pre, how = 'left', on = ['연','월','일','시'])
    print(predict_dataset)
    predict_dataset = predict_dataset.drop(['일시'],axis =1)

predict_dataset = predict_dataset[dataset.drop('혼잡도',axis=1).columns]


print(dataset.info())
print(predict_dataset.info())
dataset.to_csv(data + f'dataset_{date}.csv', index=False, encoding='utf-8-sig')
predict_dataset.to_csv(data + f'predict_dataset_{date}.csv', index=False, encoding='utf-8-sig')




