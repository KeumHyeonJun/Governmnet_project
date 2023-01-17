import pandas as pd
import datetime
import numpy as np
from pathlib import Path
import os
import warnings
import io_output

print('!!!!!!!!!!!!!!! Start visit_time.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
data = str(path) + '/data/'
result_data = str(path) + '/result_data/'

warnings.filterwarnings(action="ignore")


date = io_output.date

#### Data Load
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
df = pd.read_csv(data+"visit_time.csv")

# IQR을 활용하여 방문객 잔류 시간의 이상치 제거
def make_iqr(df):
    iqr_df = pd.DataFrame()

    site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-2","2-1"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","종합안내","6-3"],
            "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
            "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-3","복편","17-2","17-1"]}
            
    for site in list(site_dic.keys()):
        vv_ = df[df["in_site"]==site].copy()
        if len(vv_) == 0:
            iqr_df_ = pd.DataFrame({"등록일시":[datetime.datetime.now().strftime("%Y%m%d%H%M%S")],
                                "위치":[site],        
                                "평균":[0],
                                "중위수":[0],
                                "최대":[0],
                                "출입횟수":[0],
                                "이상치 개수":[0],
                                "이상치 비율":[0]})

            iqr_df = pd.concat([iqr_df,iqr_df_],axis=0)
        else:
            time_list = vv_["Time"]
            # 시간의 25%,75% 지점 -> Q1, Q3
            Q1 = np.percentile(time_list,25)
            Q3 = np.percentile(time_list,75)
            IQR = Q3-Q1
            outlier_step = 1.5 * IQR

            outlier_list = vv_[vv_["in_site"]==site][(time_list<Q1-outlier_step)|(time_list>Q3+outlier_step)].index

            iqr_df_ = pd.DataFrame({"등록일시":[datetime.datetime.now().strftime("%Y%m%d%H%M%S")],
                                    "위치":[site],        
                                    "평균":[vv_.drop(index=outlier_list)["Time"].mean()],
                                    "중위수":[vv_.drop(index=outlier_list)["Time"].median()],
                                    "최대":[vv_.drop(index=outlier_list)["Time"].max()],
                                    "출입횟수":[len(vv_)],
                                    "이상치 개수":[len(outlier_list)],
                                    "이상치 비율":[len(outlier_list)/len(vv_)]})
            # 0 days 01:14:06 -> 01:14:06 단순화
            iqr_df_["평균"] = iqr_df_["평균"].astype("timedelta64[s]").apply(lambda x : str(datetime.timedelta(seconds=x)))
            iqr_df_["중위수"] = iqr_df_["중위수"].astype("timedelta64[s]").apply(lambda x : str(datetime.timedelta(seconds=x)))
            iqr_df_["최대"] = iqr_df_["최대"].astype("timedelta64[s]").apply(lambda x : str(datetime.timedelta(seconds=x)))

            iqr_df = pd.concat([iqr_df,iqr_df_],axis=0)
    
    return iqr_df

df["Time"] = df["Time"].astype("timedelta64[s]")
iqr_df = make_iqr(df)
iqr_df = iqr_df.astype(str) 

# iqr_df.to_csv(result_data+"visit_time.csv",index=False,encoding="utf-8-sig")