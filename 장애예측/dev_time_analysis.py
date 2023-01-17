import pandas as pd
import numpy as np
import datetime
from pathlib import Path
import datetime

import warnings
import os
import dev_input_data
print('!!!!!!!!!!!!!!! time_analysis.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
raw_data = str(path) + '/raw_data/'
data = str(path) + '/data/'
result = str(path) + '/result_data/'

warnings.filterwarnings(action='ignore')

print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Start time analysis')

import query

FMSA10_작업지시_결과 = dev_input_data.FMSA10

FMSA11_작업장비이력 = dev_input_data.FMSA11

FMSB07_자재출고 = dev_input_data.FMSB07

FMSB03_자재마스터 = dev_input_data.FMSB03

FMSX04_장비계층 = dev_input_data.FMSX04

FMSX05_장비마스터 = dev_input_data.FMSX05

# 기계 = pd.read_csv(data + 'mec_finish.csv')
# 통신 = pd.read_csv(data +'tel_finish.csv')
# 방재 = pd.read_csv(data +'prevent_finish.csv')
# 승강기 = pd.read_csv(data +'elevator_finish.csv')
# 전기 = pd.read_csv(data +'electric_finish.csv')
기계 = pd.read_excel(raw_data + '수행자재_완료.xlsx', sheet_name='기계')
통신 = pd.read_excel(raw_data + '수행자재_완료.xlsx', sheet_name='통신')
방재 = pd.read_excel(raw_data + '수행자재_완료.xlsx', sheet_name='방재')
승강기 = pd.read_excel(raw_data + '수행자재_완료.xlsx', sheet_name='승강기')
전기 = pd.read_excel(raw_data + '수행자재_완료.xlsx', sheet_name='전기')

FMSX05_장비마스터.rename(columns={'class_nm_4': 'jangbi_class_nm_4'}, inplace=True)
FMSX05_장비마스터.rename(columns={'class_nm_3': 'jangbi_class_nm_3'}, inplace=True)
FMSX05_장비마스터.rename(columns={'class_nm_2': 'jangbi_class_nm_2'}, inplace=True)
FMSX05_장비마스터.rename(columns={'class_nm_1': 'jangbi_class_nm_1'}, inplace=True)

fmsa10 = FMSA10_작업지시_결과[['job_cd', 'job_nm', 'job_jisi_dt', 'job_enddt', 'job_shm', 'job_ehm']]
fmsb03 = FMSB03_자재마스터[['mat_cd', 'mat_nm']]
fmsx05 = FMSX05_장비마스터[
	['bd_cd', 'fl_cd', 'fac_cd', 'fac_nm', 'jangbi_class_nm_1', 'jangbi_class_nm_2', 'jangbi_class_nm_3',
	 'jangbi_class_nm_4', 'fac_instdt']]

jangbi = pd.merge(FMSA11_작업장비이력, fmsx05, how='inner', on='fac_cd')

jangbi_broken = pd.merge(fmsa10, jangbi, on='job_cd', how='inner')

# 오전, 오후 삭제하고 시간에 반영
# 오전, 오후가 들어있지 않은 경우는 잘못된 데이터
# jangbi_broken = jangbi_broken[(jangbi_broken['job_shm'].str.contains('오전')) | (jangbi_broken['job_shm'].str.contains('오후'))]


FMSX05_장비마스터.rename(columns={'class_nm_4': 'jangbi_class_nm_4'}, inplace=True)
FMSX05_장비마스터.rename(columns={'class_nm_3': 'jangbi_class_nm_3'}, inplace=True)
FMSX05_장비마스터.rename(columns={'class_nm_2': 'jangbi_class_nm_2'}, inplace=True)
FMSX05_장비마스터.rename(columns={'class_nm_1': 'jangbi_class_nm_1'}, inplace=True)

fmsa10 = FMSA10_작업지시_결과[['job_cd', 'job_nm', 'job_jisi_dt', 'job_enddt', 'job_shm', 'job_ehm']]
fmsb03 = FMSB03_자재마스터[['mat_cd', 'mat_nm']]
fmsx05 = FMSX05_장비마스터[
	['bd_cd', 'fl_cd', 'fac_cd', 'fac_nm', 'jangbi_class_nm_1', 'jangbi_class_nm_2', 'jangbi_class_nm_3',
	 'jangbi_class_nm_4', 'fac_instdt']]


def time_trans(x):
	date = x.split("T")[0] + " " + x.split("T")[1]
	x = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
	return x


jangbi_broken = jangbi_broken.reset_index().drop("index", axis=1)

jangbi_broken["job_start"] = jangbi_broken["job_shm"].apply(time_trans)
jangbi_broken["job_end"] = jangbi_broken["job_ehm"].apply(time_trans)

jangbi_broken["job_time"] = 0

# 작업시간 생겅하는 함수
for time in range(len(jangbi_broken)):
	jangbi_broken.loc[time, "job_time"] = jangbi_broken.loc[time, "job_end"] - jangbi_broken.loc[time, "job_start"]

# 필요한 컬럼만 추출
# 일/ 시간/분 > 분으로 환산
time_data = jangbi_broken[
	['jangbi_class_nm_1', 'jangbi_class_nm_2', 'jangbi_class_nm_3', 'jangbi_class_nm_4', 'job_time']]
# time_data['job_class_nm_4'].dt.days
time_data['job_time'] = time_data['job_time'].astype(str)
time_data['일'] = time_data['job_time'].str[:-13]
time_data = time_data[~time_data['일'].str.contains('-')]
time_data['시간'] = time_data['job_time'].str[-8:]
time_data['시'] = pd.to_datetime(time_data['시간']).dt.hour
time_data['분'] = pd.to_datetime(time_data['시간']).dt.minute
time_data[['일', '시', '분']] = time_data[['일', '시', '분']].astype(int)
time_data['총시간'] = time_data['일'] * 24 * 60 + time_data['시'] * 60 + time_data['분']

# 수행범위(행안부 지정) 파일 + 장비별 작업 시간 계산 join
수행범위 = pd.concat([기계, 통신, 방재, 승강기, 전기])
time_data = pd.merge(time_data, 수행범위,
					 left_on=['jangbi_class_nm_1', 'jangbi_class_nm_2', 'jangbi_class_nm_3', 'jangbi_class_nm_4'],
					 right_on=['Lv1', 'Lv2', 'Lv3', 'Lv4'], how='left')

# 행안부의 그룹정의별 중위, 평군, 최대, 최소 계산
time_final_median = time_data.groupby('그룹정의').median()['총시간']
time_final_median = time_final_median.reset_index()

time_final_mean = time_data.groupby('그룹정의').mean()['총시간']
time_final_mean = time_final_mean.reset_index()

time_final_max = time_data.groupby('그룹정의').max()['총시간']
time_final_max = time_final_max.reset_index()

time_final_min = time_data.groupby('그룹정의').min()['총시간']
time_final_min = time_final_min.reset_index()

final = pd.concat([time_final_median, time_final_mean['총시간'], time_final_max['총시간'], time_final_min['총시간']], axis=1)
final['등록일시'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
final = final.astype(str)
final['그룹정의'] = final['그룹정의'].apply(lambda x: 'z' if x == '0' else str(x))
final.columns = ['그룹정의', '중위', '평균', '최대', '최소', '등록일시']
result_time_alalysis = final
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Finish time analysis')

# final.to_csv(result + '작업시간.csv',index = False , encoding='utf-8-sig')