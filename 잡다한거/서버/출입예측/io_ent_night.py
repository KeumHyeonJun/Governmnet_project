import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
import os
import warnings
import io_output

print('!!!!!!!!!!!!!!! Start ent_night.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
data = str(path) + '/data/'
result = str(path) + '/result_data/'

warnings.filterwarnings(action='ignore')

date = io_output.date

# 데이터 로드
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
ent_night = pd.read_csv(data+"ent_night.csv")

site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-1","2-2"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","6-3","종합안내"],
            "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
            "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-1","17-3","복편","17-2"]}


# 선택한 날짜 이전 한달 간의 데이터만 사용
night_hour = pd.DataFrame()
ent_night["msgtime"] = ent_night["msgtime"].astype("datetime64")
ent_night = ent_night[(ent_night["msgtime"] >= (datetime.datetime.strptime(date,"%Y%m%d") - relativedelta(months=1))) & (ent_night["msgtime"] < datetime.datetime.strptime(date,"%Y%m%d"))]
# 야간시간대: 23~06
# 동별, 시간대별 야간시간대 평균 출입 인원 수 산출
night_hour = pd.DataFrame()

for site in site_dic.keys():
    en = ent_night[ent_night["inout_site_no"]==site]
    en["day"] = en["msgtime"].apply(lambda x: str(x)[:10]).astype("datetime64")
    en = round(en["hour"].value_counts() / (en["day"].max() - en["day"].min()).days).astype("int64")
    en = pd.merge(pd.DataFrame(index=[23,0,1,2,3,4,5]),en,left_index=True,right_index=True,how="left")
    en["site"] = site
    night_hour = pd.concat([night_hour,en],axis=0)
    night_hour.fillna(0,inplace=True)

night_hour.reset_index(inplace=True)
night_hour.rename(columns={"index":"시간대","hour":"일평균 출입인원수","site":'위치'},inplace=True)
night_hour.loc[:,"등록일시"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
night_hour = night_hour[["등록일시","위치","시간대","일평균 출입인원수"]]

night_hour = night_hour.astype(str)


night_door = pd.DataFrame()
# 동별, 출입구별 취약시간대 평균 출입 인원 수 산출
for site in site_dic.keys():
    es = ent_night[ent_night["inout_site_no"]==site]
    es["day"] = es["msgtime"].apply(lambda x: str(x)[:10]).astype("datetime64")
    es = round(es["reader_nm"].apply(lambda x : x.split("스피드")[0]).value_counts() / (es["day"].max() - es["day"].min()).days).astype("int64")

    night_door = pd.concat([night_door,pd.DataFrame({"위치":site,"일평균 출입인원수":es})])
night_door.reset_index(inplace=True)
night_door.rename(columns={"index":"출입구"},inplace=True)
night_door.loc[:,"등록일시"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
night_door = night_door[["등록일시","위치","출입구","일평균 출입인원수"]]
night_door = night_door.astype(str)
#night_hour
#night_door

# night_hour.to_csv(result+"night_hour.csv",index=False,encoding="utf-8-sig")
# night_door.to_csv(result+"night_door.csv",index=False,encoding="utf-8-sig")