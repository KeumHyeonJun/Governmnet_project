import pandas as pd
from pathlib import Path
from lifelines import KaplanMeierFitter
import datetime
import warnings
import os
from pathlib import Path

import dev_input_data

print('!!!!!!!!!!!!!!! equipment_analysis.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
raw_data = str(path) + '/raw_data/'
data_path = str(path) + '/data/'
result = str(path) + '/result_data/'

warnings.filterwarnings(action='ignore')

# 데이터 Load
data = dev_input_data.input_data
data=data[data['장애분석']!= 'X']


# 간단한 전처리
broken = data[data['status']==1]
cnt = broken['fac_cd'].value_counts()

# 작업을 한번'만' 한 경우
first = list(cnt[cnt==1].index)
first_df = pd.DataFrame({'fac_cd':first})
# 작업을 한번 이상 한 장비 중 첫번째 작업 정보
first_df_2 = data[data['job_cnt']==1]

# 작업을 두번'만' 한 장비
second = list(cnt[cnt==2].index)
second_df = pd.DataFrame({'fac_cd':second})

#작업을 두번 이상 한 장비 중 두번째 작업 정보
second_df_2 = data[data['job_cnt']==2]

# 작업을 세번이상 한 경우
third_df_2 = data[data['job_cnt']>=3]

first_df = pd.merge(first_df,data,on='fac_cd',how='left')
second_df = pd.merge(second_df,data,on='fac_cd',how='left')

predict_cnt_1 = pd.concat([first_df,second_df_2],axis=0)

predict_cnt_2 = pd.concat([second_df,third_df_2],axis=0)
predict_cnt_2 = predict_cnt_2[predict_cnt_2['job_cnt']>=2]
def status_1(df):
    if df['job_cnt'] == 1:
        return 0
    else :
        return 1

def status_2(df):
    if df['job_cnt'] == 2:
        return 0
    else :
        return 1

def input_time(df):
    if df['status'] ==1 :
        return df['job_job']
    else :
        return df['time']

predict_cnt_1['status'] = predict_cnt_1.apply(status_1,axis=1)
predict_cnt_1['input_time'] = predict_cnt_1.apply(input_time,axis=1)
predict_cnt_2['status'] = predict_cnt_2.apply(status_2,axis=1)
predict_cnt_2['input_time'] = predict_cnt_2.apply(input_time,axis=1)


# 1. 그룸 정의 별로 학습하기
# 2. 각 장비별로 인풋값에 넣기
# 3. 두번 이상 고장난 경우 > status 다르게 해서 봐야함 2번 고장만 난 경우 > 0 3번이상 고장 난 경우 >1


def kplan(그룹정의):
    output_data = pd.DataFrame({
    '대분류' : [],
    '장비분류' :[],
    '동':[],
    '층' :[],
    '장비코드' :[],
    '장비명' : [],
    '장애발생횟수' :[],
    '최근장애일자' :[],
    '7일이내장애확률' :[],
    '30일이내장애확률':[],
    'Lv4':[]
})


    input_data = data[data['그룹정의']==그룹정의]
    # 이때까지 장애가 발생하지 않은 경우 > 처음 발생 하는 확률 찾기
    input_first = input_data[input_data['job_cnt']<=1]
    if len(input_first) >=2:
        kmf_first= KaplanMeierFitter()
        var_first = 0
        input_first.sort_values(by='job_job', ascending=True)
        kmf_first.fit(durations=input_first['job_job'], event_observed=input_first['status'])

    # job_cnt = 2 인 경우 > 장애가 한번 발생한 장비의 다음 장비 예측하기
    input_second = predict_cnt_1[predict_cnt_1['그룹정의']==그룹정의]
    if len(input_second) >=2:
        kmf_second= KaplanMeierFitter()
        var_second = 0
        input_second.sort_values(by='input_time', ascending=True)
        kmf_second.fit(durations=input_second['input_time'], event_observed=input_second['status'])

    # job_cnt >=3 인 경우 > 재발한 장비의 다음 장비 예측하기

    input_third = predict_cnt_2[predict_cnt_2['그룹정의']==그룹정의]
    if len(input_third) >=2:
        kmf_third= KaplanMeierFitter()
        var_third = 0
        input_third.sort_values(by='input_time', ascending=True)
        kmf_third.fit(durations=input_third['input_time'], event_observed=input_third['status'])

    fac_list = list(input_data['fac_cd'].unique())

    # 작업을 한번 한경우, 두번한경우, 세번이상 한 경우에 따라서 다르게 예측
    if 'var_first' in locals():
        var_first = True
    else :
        var_first = False

    if 'var_second' in locals():
        var_second = True
    else :
        var_second = False

    if 'var_third' in locals():
        var_third = True
    else :
        var_third = False


    
    for i in fac_list:
        df = input_data[input_data['fac_cd']==i].iloc[-1]
        seven = df['time'] +7
        thirty = seven + 23
        new_data = []
        new_data.append(df['Lv1'])
        new_data.append(df['그룹정의'])
        new_data.append(df['bd_nm'])
        new_data.append(df['fl_cd'])
        new_data.append(df['fac_cd'])
        new_data.append(df['fac_nm'])
        new_data.append(df['job_cnt'])
        new_data.append(df['job_jisi_dt'])
       # 7일 이내 고장 확률
        if df['job_cnt'] == 0 and var_first == True:
            new_data.append(1-kmf_first.predict(seven))

        elif df['job_cnt'] ==1 and var_second == True:
            new_data.append(1-kmf_second.predict(seven))
        elif df['job_cnt'] ==1 and var_first == True:
            new_data.append(1-kmf_first.predict(seven))

        elif df['job_cnt'] >=2 and var_third == True:
            new_data.append(1-kmf_third.predict(seven))
            
        elif df['job_cnt'] >=2 and var_second == True:
            new_data.append(1-kmf_second.predict(seven))
            
        elif df['job_cnt'] >=2 and var_first == True:
            new_data.append(1-kmf_first.predict(seven))
        else :
            new_data.append(99999)

        # 30일 이내 고장 확률
        if df['job_cnt'] == 0 and var_first == True:
            new_data.append(1-kmf_first.predict(thirty))

        elif df['job_cnt'] ==1 and var_second == True:
            new_data.append(1-kmf_second.predict(thirty))
        elif df['job_cnt'] ==1 and var_first == True:
            new_data.append(1-kmf_first.predict(thirty))

        elif df['job_cnt'] >=2 and var_third == True:
            new_data.append(1-kmf_third.predict(thirty))
        elif df['job_cnt'] >=2 and var_second == True:
            new_data.append(1-kmf_second.predict(thirty))
        elif df['job_cnt'] >=2 and var_first == True:
            new_data.append(1-kmf_first.predict(thirty))
        else :
            new_data.append(99999)
        new_data.append(df['Lv4'])

        output_data.loc[len(output_data)] = new_data

    return output_data


group = list(data['그룹정의'].unique())
output_data = pd.DataFrame({
    '대분류' : [],
    '장비분류' :[],
    '동':[],
    '층' :[],
    '장비코드' :[],
    '장비명' : [],
    '장애발생횟수' :[],
    '최근장애일자' :[],
    '7일이내장애확률' :[],
    '30일이내장애확률':[],
    'Lv4':[]
})
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Start survival analysis')

for i in group:
    output = kplan(i)
    output_data = pd.concat([output_data,output],axis=0)
output_data = output_data.drop_duplicates()
output_data = output_data.drop(['Lv4'],axis=1)
output_data['등록일시'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
output_data = output_data.astype(str)
output_data['동'] = output_data['동'].apply(lambda x: 'z' if x =='0' else str(x))
output_data['층'] = output_data['층'].apply(lambda x: 'z' if x =='0' else str(x))
output_data.fillna('z')
result_equipment_analysis = output_data
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Finish survival analysis')

#output_data.to_csv(result + '생존분석결과.csv',index = False, encoding = 'utf-8-sig')