import pandas as pd
import datetime
import numpy as np
from pathlib import Path
import os
import warnings
import holidays
from dateutil.relativedelta import relativedelta
import pandas as pd
from impala.dbapi import connect
from impala.util import as_pandas

import io_output
import config

warnings.filterwarnings(action="ignore")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
data = str(path) + '/data/'
result_data = str(path) + '/data/'


if not os.path.exists(str(path)+'/data/'):
    os.makedirs(str(path)+'/data/')


date = io_output.date

# 스피드 게이트 이름을 통해 해당 동을 반환하는 함수
def find_key(site_dic, x):
    return [key for key,value in site_dic.items() if x in value][0]


kr_holidays = holidays.KR()
satsun = ['Independence Movement Day','Liberation Day','National Foundation Day','Hangeul Day',"Children's Day"]
def alternative_holiday(date):
    if date in kr_holidays:
        return 1
    elif date.weekday() == 0:
        if (kr_holidays.get(datetime.datetime.strftime(date-relativedelta(days=1),"%Y-%m-%d")) or kr_holidays.get(datetime.datetime.strftime(date-relativedelta(days=2),"%Y-%m-%d"))) in satsun:
            return 1
        else:
            return 0
    else:
        return 0



# IN/OUT이 연속해서 나타나는 데이터 전처리 함수
def inout_df(df):
    df_ = df.copy()
    df_ = df_.dropna()
    df_ = df_.reset_index(drop=True)
    ind = 0

    # company_nm 별 데이터프레임 생성
    for com in df_["company_nm"].unique():
        df__ = df_[df_["company_nm"]==com]
        df__ = df__.reset_index(drop=True)
        # IN이나 OUT이 하나라도 0일 경우 이상치로 설정
        if (len(df__[df__["INOUT"]=="IN"]) == 0) | (len(df__[df__["INOUT"]=="OUT"])==0):
            return pd.DataFrame()

        while True:
            # IN과 OUT이 한 번씩 번갈아 들장하면 정상 진행
            if df__.loc[ind,"INOUT"] != df__.loc[ind+1,"INOUT"]:
                ind += 1
            else:
                # IN이 연속해서 등장할 경우 가장 마지막 IN만 사용
                if df__.loc[ind,"INOUT"] == "IN":
                    df__ = df__.drop(index=ind,axis=0)
                    df__ = df__.reset_index(drop=True)
                # OUT이 연속해서 등장할 경우 가장 첫번째 OUT만 사용
                else:
                    df__ = df__.drop(index=ind+1,axis=0)
                    df__ = df__.reset_index(drop=True)
            if ind+1 == len(df__):
                return df__

# IN/OUT을 처리한 데이터에서 OUT-IN으로 잔류 시간을 추출하는 함수
def make_df(df):
    ind = 0
    c = pd.DataFrame()
    # DataFrame이 None인 경우, 길이가 0인 경우가 존재했기 때문에 해당 조건을 만족할 경우 빈 DataFrame return
    if df is None:
        return c
    elif len(df) == 0:
        return c
    else:
        df = df.reset_index(drop=True)

    # OUT으로 시작할 경우 삭제 -> 반드시 IN으로 시작
    if df.loc[0,"INOUT"] == "OUT":
        df = df.drop(index=0,axis=0)
        df = df.reset_index(drop=True)
    # IN으로 끝날 경우 삭제 -> 반드시 OUT으로 끝
    if df.loc[len(df)-1,"INOUT"] == "IN":
        df = df.drop(index=len(df)-1,axis=0)
        df = df.reset_index(drop=True)

    if len(df) == 0:
        return c

    while True:
        # Time: 잔류 시간, reader_nm_in: 진입 출입문 명, reader_nm_out: 진출 출입문 명, in_site: 진입 동, out_site: 진출 동
        b = pd.DataFrame({"Time":[df.loc[ind+1,"msgtime"]-df.loc[ind,"msgtime"]],"reader_nm_in":[df.loc[ind,"reader_nm"]], \
                        "reader_nm_out":[df.loc[ind+1,"reader_nm"]],"in_site":[df.loc[ind,"inout_site"]],"out_site":[df.loc[ind+1,"inout_site"]]})
        c = pd.concat([c,b],axis=0)
        ind += 2

        if ind == len(df):
            return c

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



site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-2","2-1"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","종합안내","6-3"],
            "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
            "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-3","복편","17-2","17-1"]}



# # weather
# print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - weather')
# # conn = connect(host = '172.31.101.61', port = 21050 , user = 'hive', password = 'hive')
# conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
# create_query ='select * from SVC.ext_kma_asos_hourly_info_nopartition'
# # run query on impala
# cur = conn.cursor()
# cur.execute(create_query)
# weather_his = as_pandas(cur)

# # conn = connect(host = '172.31.101.61', port = 21050 , user = 'hive', password = 'hive')
# conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
# create_query ='select * from SVC.ext_kma_vilage_fcst_nopartition'
# # run query on impala
# cur = conn.cursor()
# cur.execute(create_query)
# weather_pre = as_pandas(cur)
# cur.close()

# 예보데이터
# print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Preprocessing Data - weather')
# df_tmp = weather_pre[weather_pre["category"]=="TMP"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
#     "fcstdate":"일시","fcsttime":"시간","fcstvalue":"기온(°C)"})
# df_pcp = weather_pre[weather_pre["category"]=="PCP"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
#     "fcstdate":"일시","fcsttime":"시간","fcstvalue":"강수량(mm)"})
# df_wsd = weather_pre[weather_pre["category"]=="WSD"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
#     "fcstdate":"일시","fcsttime":"시간","fcstvalue":"풍속(m/s)"})
# df_reh = weather_pre[weather_pre["category"]=="REH"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
#     "fcstdate":"일시","fcsttime":"시간","fcstvalue":"습도(%)"})
# df_sno = weather_pre[weather_pre["category"]=="SNO"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
#     "fcstdate":"일시","fcsttime":"시간","fcstvalue":"적설(cm)"})

# df_pcp.loc[df_pcp["강수량(mm)"]=="강수없음","강수량(mm)"] = 0
# df_sno.loc[df_sno["적설(cm)"]=="적설없음","적설(cm)"] = 0

# final_df = df_tmp.copy()
# final_df = pd.merge(final_df,df_pcp,on=["일시","시간"],how="left")
# final_df = pd.merge(final_df,df_wsd,on=["일시","시간"],how="left")
# final_df = pd.merge(final_df,df_reh,on=["일시","시간"],how="left")
# final_df = pd.merge(final_df,df_sno,on=["일시","시간"],how="left")

# for ind in range(len(final_df)):
#     # final_df.loc[ind, "일시"] = datetime.datetime.strptime(final_df.loc[ind,"일시"][:4]+"-"+final_df.loc[ind,"일시"][4:6]+"-"+final_df.loc[ind,"일시"][6:]+" "+final_df.loc[ind,"시간"][:2],"%Y-%m-%d %H")
#     # from datetime import datetime으로 바뀌었음 —> datetime.datetime을 datetime으로 변경
#     final_df.loc[ind, "일시"] = datetime.datetime.strptime(final_df.loc[ind,"일시"][:4]+"-"+final_df.loc[ind,"일시"][4:6]+"-"+final_df.loc[ind,"일시"][6:]+" "+final_df.loc[ind,"시간"][:2],"%Y-%m-%d %H")

# weather_pre = final_df.drop("시간",axis=1)
# weather_pre['적설(cm)'] = weather_pre.apply(replace_snow,axis=1)
# weather_pre['강수량(mm)'] = weather_pre.apply(replace_rain,axis=1)
# #과거데이터
# weather_his = weather_his[['tm','ta','rn','ws','hm','dsnw']]
# weather_his.replace('',0,inplace=True)

# weather_his.columns = weather_pre.columns

conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
create_query ='select * from SVC.ext_kma_asos_hourly_info'
# run query on impala
cur = conn.cursor()
cur.execute(create_query)
weather_his = as_pandas(cur)
weather_his = weather_his.sort_values(by='tm')

create_query ='select * from SVC.ext_kma_vilage_fcst'
# run query on impala
cur = conn.cursor()
cur.execute(create_query)
weather_pre = as_pandas(cur)
cur.close()

# 예보데이터
df_tmp = weather_pre[weather_pre["category"]=="TMP"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"기온(°C)"})
df_pcp = weather_pre[weather_pre["category"]=="PCP"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"강수량(mm)"})
df_wsd = weather_pre[weather_pre["category"]=="WSD"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"풍속(m/s)"})
df_reh = weather_pre[weather_pre["category"]=="REH"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
    "fcstdate":"일시","fcsttime":"시간","fcstvalue":"습도(%)"})
df_sno = weather_pre[weather_pre["category"]=="SNO"][["fcstdate","fcsttime","fcstvalue"]].rename(columns={
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

weather_pre = final_df.drop("시간",axis=1)
weather_pre['적설(cm)'] = weather_pre.apply(replace_snow,axis=1)
weather_pre['강수량(mm)'] = weather_pre.apply(replace_rain,axis=1)
#과거데이터 
weather_his = weather_his[['tm','ta','rn','ws','hm','dsnw']]
weather_his.replace('',0,inplace=True)

weather_his.columns = weather_pre.columns

# weather_his = pd.read_csv('whether_his1.csv')
# weather_pre = pd.read_csv('whether_pre1.csv')
# weather_his['일시'] = pd.to_datetime(weather_his['일시'])
# weather_pre['일시'] = pd.to_datetime(weather_pre['일시'])

weather_his["일시"] = weather_his["일시"].astype("datetime64")
weather_his["weekday"] = weather_his["일시"].apply(lambda x : x.weekday())
weather_his["holiday"] = weather_his["일시"].apply(alternative_holiday)
weather_his["시간"] = weather_his["일시"].apply(lambda x : x.hour)
weather_his["년도"] = weather_his["일시"].apply(lambda x : x.year)
weather_his["월"] = weather_his["일시"].apply(lambda x : x.month)
weather_his["일"] = weather_his["일시"].apply(lambda x : x.day)

weather_pre["일시"] = weather_pre["일시"].astype("datetime64")
weather_pre["weekday"] = weather_pre["일시"].apply(lambda x : x.weekday())
weather_pre["holiday"] = weather_pre["일시"].apply(alternative_holiday)
weather_pre["시간"] = weather_pre["일시"].apply(lambda x : x.hour)
weather_pre["년도"] = weather_pre["일시"].apply(lambda x : x.year)
weather_pre["월"] = weather_pre["일시"].apply(lambda x : x.month)
weather_pre["일"] = weather_pre["일시"].apply(lambda x : x.day)

weather_his.to_csv(data+"weather_his.csv",encoding="utf-8-sig",index=False)
weather_pre.to_csv(data+"weather_pre.csv",encoding="utf-8-sig",index=False)


# predict_data


set_time = pd.date_range(date, date+"2300", freq='h')
predict_data = pd.DataFrame({"일시":set_time})
if datetime.datetime.strptime(date,"%Y%m%d") <= weather_his["일시"].max():
    weather_pre_data = weather_his[(weather_his["일시"]>=datetime.datetime.strptime(date,"%Y%m%d")) & (weather_his["일시"]<datetime.datetime.strptime(str(int(date)+1),"%Y%m%d"))]
else:
    weather_pre_data = weather_pre[(weather_pre["일시"]>=datetime.datetime.strptime(date,"%Y%m%d")) & (weather_pre["일시"]<datetime.datetime.strptime(str(int(date)+1),"%Y%m%d"))]
predict_data = pd.merge(predict_data,weather_pre_data,on="일시",how="left")


if (predict_data["월"][0]==1) and (predict_data["일"][0] == 1):
    null_date = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x - relativedelta(years=1) -relativedelta(days=1))
null_date = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x - relativedelta(years=1))
alternative_date = pd.merge(weather_his,null_date,on="일시",how="inner")[["기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)"]]

predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,"weekday"] = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x.weekday())
predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,"holiday"] = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(alternative_holiday)
predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,"시간"] = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x.hour)
predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,"년도"] = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x.year)
predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,"월"] = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x.month)
predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,"일"] = predict_data[predict_data["기온(°C)"].isnull()]["일시"].apply(lambda x : x.day)
predict_data.loc[predict_data[predict_data["기온(°C)"].isnull()].index,["기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)"]] = alternative_date

predict_data.to_csv(data+"predict_data.csv",encoding="utf-8-sig",index=False)


# visit_in, visit_out
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - visit')

# conn = connect(host="172.31.101.61",port=21050,user="hive",password="hive")
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
cursor = conn.cursor()

query = '''
SELECT reader_nm, emp_no, company_nm, msgTime 
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" AND emptype_nm = "방문객" 
    and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 1 YEAR), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
'''
cursor.execute(query)
visit = as_pandas(cursor)
cursor.close
conn.close

print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Preprocessing Data - visit')
visit["msgtime"] = visit["msgtime"].astype("datetime64")
visit["INOUT"] = visit["reader_nm"].apply(lambda x : "IN" if ("IN" in x) | ("입구" in x) else "OUT")
visit["inout_site"] = visit["reader_nm"].apply(lambda x : x.split("동")[0])
visit["inout_site"] = visit["inout_site"].apply(lambda x : x.split()[0])
visit = visit.sort_values("msgtime")
visit = visit.reset_index(drop=True)
visit["inout_site_no"] = visit["inout_site"].apply(lambda x : find_key(site_dic,x))
visit.drop(index = visit[visit["company_nm"]==""].index, axis=0, inplace=True)

# visit_company_in, visit_company_out
df = pd.DataFrame()
for site in site_dic.keys():
    df_ = pd.DataFrame({"site":int(site.split("동")[0]),"company":visit[visit["inout_site_no"]==site]["company_nm"].unique()})
    df = pd.concat([df,df_])
    
df.reset_index(inplace=True,drop=True)
df.reset_index(inplace=True)
df.rename(columns={"index":"label"},inplace=True)

visit_company_in = pd.DataFrame()
visit_company_out = pd.DataFrame()

for site in site_dic.keys():
    vv = visit.copy()
    vis = vv[["inout_site_no","msgtime","INOUT","company_nm"]]
    
    visit_in_final_ = pd.DataFrame()
    visit_out_final_ = pd.DataFrame()
    visit_ = vis[vis["inout_site_no"]==site]
    for company in visit_["company_nm"].unique():
        visit_in = visit_[(visit_["INOUT"]=="IN") & (visit_["company_nm"]==company)]
        set_time = pd.date_range(datetime.datetime.strftime(visit_["msgtime"].min(),"%Y%m%d"), datetime.datetime.strftime(visit_["msgtime"].max(),"%Y%m%d%H")+"0000", freq='h')
        visit_in_final = pd.DataFrame(index=set_time)
        visit_in["msgtime"] = visit_in["msgtime"].apply(lambda x: datetime.datetime.strptime(str(x)[:13],"%Y-%m-%d %H"))
        visit_in = visit_in.groupby("msgtime").agg({"inout_site_no":np.size})
        visit_in_final = pd.merge(visit_in_final, visit_in, left_index=True, right_index=True, how="left")
        visit_in_final.index.freq = "h"
        visit_in_final = pd.merge(visit_in_final,weather_his.set_index("일시"),left_index=True,right_index=True,how="left")
        visit_in_final = visit_in_final.fillna(0)
        visit_in_final = visit_in_final.astype("float64")
        visit_in_final = visit_in_final.reset_index()
        visit_in_final["weekday"] = visit_in_final["index"].apply(lambda x : x.weekday())
        visit_in_final["holiday"] = visit_in_final["index"].apply(alternative_holiday)
        visit_in_final["시간"] = visit_in_final["index"].apply(lambda x: x.hour)
        visit_in_final["년도"] = visit_in_final["index"].apply(lambda x: x.year)
        visit_in_final["월"] = visit_in_final["index"].apply(lambda x: x.month)
        visit_in_final["일"] = visit_in_final["index"].apply(lambda x: x.day)
        visit_in_final = visit_in_final.set_index("index")
        visit_in_final["company"] = company
        visit_in_final_ = pd.concat([visit_in_final_,visit_in_final])

    for company in visit_["company_nm"].unique():
        visit_out = visit_[(visit_["INOUT"]=="OUT") & (visit_["company_nm"]==company)]
        set_time = pd.date_range(datetime.datetime.strftime(visit_["msgtime"].min(),"%Y%m%d"), datetime.datetime.strftime(visit_["msgtime"].max(),"%Y%m%d%H")+"0000", freq='h')
        visit_out_final = pd.DataFrame(index=set_time)
        visit_out["msgtime"] = visit_out["msgtime"].apply(lambda x: datetime.datetime.strptime(str(x)[:13],"%Y-%m-%d %H"))
        visit_out = visit_out.groupby("msgtime").agg({"inout_site_no":np.size})
        visit_out_final = pd.merge(visit_out_final, visit_out, left_index=True, right_index=True, how="left")
        visit_out_final.index.freq = "h"
        visit_out_final = pd.merge(visit_out_final,weather_his.set_index("일시"),left_index=True,right_index=True,how="left")
        visit_out_final = visit_out_final.fillna(0)
        visit_out_final = visit_out_final.astype("float64")
        visit_out_final = visit_out_final.reset_index()
        visit_out_final["weekday"] = visit_out_final["index"].apply(lambda x : x.weekday())
        visit_out_final["holiday"] = visit_out_final["index"].apply(alternative_holiday)
        visit_out_final["시간"] = visit_out_final["index"].apply(lambda x: x.hour)
        visit_out_final["년도"] = visit_out_final["index"].apply(lambda x: x.year)
        visit_out_final["월"] = visit_out_final["index"].apply(lambda x: x.month)
        visit_out_final["일"] = visit_out_final["index"].apply(lambda x: x.day)
        visit_out_final = visit_out_final.set_index("index")
        visit_out_final["company"] = company
        visit_out_final_ = pd.concat([visit_out_final_,visit_out_final])

        visit_in_final_["site"] = int(site.split("동")[0])
        visit_out_final_["site"] = int(site.split("동")[0])

    visit_company_in = pd.concat([visit_company_in,visit_in_final_])
    visit_company_out = pd.concat([visit_company_out,visit_out_final_])
    print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), f'Finish site {site}')

visit_company_in_ = pd.merge(visit_company_in,df,left_on=["company","site"],right_on=["company","site"],how="left")
visit_company_out_ = pd.merge(visit_company_out,df,left_on=["company","site"],right_on=["company","site"],how="left")

visit_company_in_.index = visit_company_in.index
visit_company_out_.index = visit_company_out.index

visit_company_in_ = visit_company_in_.reset_index()[["index","inout_site_no","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site","company","label"]]
visit_company_out_ = visit_company_out_.reset_index()[["index","inout_site_no","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site","company","label"]]

df.to_csv(data+"company_label.csv",encoding="utf_8-sig",index=False)
visit_company_in_.to_csv(data+"visit_company_in.csv",encoding="utf-8-sig",index=False)
visit_company_out_.to_csv(data+"visit_company_out.csv",encoding="utf-8-sig",index=False)



# visit_in, visit_out
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), "Processing visit_inout")
visit_in = visit_company_in_.groupby(["index","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site"]).agg({"inout_site_no":np.sum}).reset_index().sort_values(["site","index"]).reset_index(drop=True)
visit_out = visit_company_out_.groupby(["index","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site"]).agg({"inout_site_no":np.sum}).reset_index().sort_values(["site","index"]).reset_index(drop=True)
visit_in = visit_in[["index","inout_site_no","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site"]]
visit_out = visit_out[["index","inout_site_no","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site"]]


visit_in.to_csv(data+"visit_in.csv",encoding="utf-8-sig",index=False)
visit_out.to_csv(data+"visit_out.csv",encoding="utf-8-sig",index=False)



# visit time
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), "Processing visit_time")
vis_f = pd.DataFrame()
# 방문객 사원번호(n동 m번 카드)를 통해 in/out이 반복되는 데이터 처리 후, 쟌류 시간 계산
for emp in visit["emp_no"].unique():
    df = visit[visit["emp_no"]==emp]
    df = inout_df(df)
    df = make_df(df)
    vis_f = pd.concat([vis_f,df],axis=0)

vis_f = vis_f.reset_index(drop=True)
# find_key 함수를 통해 진입, 진출 동 반환
vis_f["in_site"] = vis_f["in_site"].apply(lambda x : find_key(site_dic,x))
vis_f["out_site"] = vis_f["out_site"].apply(lambda x : find_key(site_dic,x))
# 동 별 잔류시간을 확인하기 위해 IN과 OUT이 동일한 데이터만 사용
vv = vis_f[vis_f["in_site"]==vis_f["out_site"]]
# 60초 이하의 데이터는 이상치로 간주하여 삭제
ind_60 = vv[vv["Time"] < datetime.timedelta(seconds=60)].index
vv = vv.drop(index=ind_60).reset_index(drop=True)

vv.to_csv(data+"visit_time.csv",encoding="utf-8-sig",index=False)





print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - ratio')
# conn = connect(host="172.31.101.61",port=21050,user="hive",password="hive")
conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
cursor = conn.cursor()

query = '''
SELECT reader_nm, emptype_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 1 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
'''
cursor.execute(query)
ent = as_pandas(cursor)
cursor.close
conn.close


print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Preprocessing Data - ratio')
# visit_ratio, emp_ratio
all_inout = ent.copy()
all_inout["msgtime"] = all_inout["msgtime"].astype("datetime64")
# 선택한 날짜 이전 한달간의 데이터 사용
all_inout = all_inout[(all_inout["msgtime"] >= (datetime.datetime.strptime(date,"%Y%m%d") - relativedelta(months=1))) & (all_inout["msgtime"] < datetime.datetime.strptime(date,"%Y%m%d"))]
# emptype_nm 공무원과 방문객으로 구분
visit = all_inout[all_inout["emptype_nm"]=="방문객"]
gong = all_inout[all_inout["emptype_nm"]=="공무원"]

visit["msgtime"] = visit["msgtime"].astype("datetime64")
visit["INOUT"] = visit["reader_nm"].apply(lambda x : "IN" if ("IN" in x) | ("입구" in x) else "OUT")
visit["inout_site"] = visit["reader_nm"].apply(lambda x : x.split("동")[0])
visit["inout_site"] = visit["inout_site"].apply(lambda x : x.split()[0])
visit = visit.reset_index(drop=True)
visit["inout_site_no"] = visit["inout_site"].apply(lambda x : find_key(site_dic, x))

gong["msgtime"] = gong["msgtime"].astype("datetime64")
gong["INOUT"] = gong["reader_nm"].apply(lambda x : "IN" if ("IN" in x) | ("입구" in x) else "OUT")
gong["inout_site"] = gong["reader_nm"].apply(lambda x : x.split("동")[0])
gong["inout_site"] = gong["inout_site"].apply(lambda x : x.split()[0])
gong = gong.reset_index(drop=True)
gong["inout_site_no"] = gong["inout_site"].apply(lambda x : find_key(site_dic, x))

visit.to_csv(data+"visit_ratio.csv",encoding="utf-8-sig",index=False)
gong.to_csv(data+"emp_ratio.csv",encoding="utf-8-sig",index=False)



# emp_night
ent_ = ent.copy()

ent_["inout_site"] = ent_["reader_nm"].apply(lambda x : x.split("동")[0])
ent_["inout_site"] = ent_["inout_site"].apply(lambda x : x.split()[0])
ent_["inout_site_no"] = ent_["inout_site"].apply(lambda x: find_key(site_dic,x))
# 야간 시간대 --> 23시~06시
ent_["hour"] = ent_["msgtime"].apply(lambda x: x[11:13])
ent_["hour"] = ent_["hour"].astype("int64")
ent_night = ent_[(ent_["hour"]<6) | (ent_["hour"]==23)]

ent_night.to_csv(data+"ent_night.csv",encoding="utf-8-sig",index=False)


# all_in, all_out
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load and Preprocessing Data - all')
all_in = pd.DataFrame()
all_out = pd.DataFrame()

for site in site_dic.keys():
    import io_query

    print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), f'Load Data - all enter {site}')
    # conn = connect(host="172.31.101.61",port=21050,user="hive",password="hive")
    conn = connect(host = config.host, port = config.port , user = config.user, password = config.password)
    cursor = conn.cursor()

    query = io_query.query_dic[site]
    cursor.execute(query)
    enter_ = as_pandas(cursor)
    cursor.close
    conn.close

    print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), f'Preprocessing Data - all enter {site}')
    enter_["msgtime"] = enter_["msgtime"].astype("datetime64")
    # 출입문 이름을 통해 IN/OUT을 구분하는 INOUT 컬럼 생성
    enter_["INOUT"] = enter_["reader_nm"].apply(lambda x : "IN" if ("IN" in x) | ("입구" in x) else "OUT")
    # 출입문 이름을 통해 출입 동을 구분하는 inout_site 컬럼 생성
    enter_["inout_site"] = enter_["reader_nm"].apply(lambda x : x.split("동")[0])
    enter_["inout_site"] = enter_["inout_site"].apply(lambda x : x.split()[0])
    # 출입문을 통해 출입 동을 구분
    # 1동에는 1동 스피드게이트, 1-A동 스피드게이트 등 동을 같은 동에 대해서도 여러가지 형태로 나타나 있기 때문에 하나의 동으로 묶기 위해 Dictionary 생성
    site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-2","2-1"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","종합안내","6-3"],
                "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
                "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-3","복편","17-2","17-1"]}
    # 출입기록 시간 순으로 데이터 정렬
    enter_ = enter_.sort_values("msgtime")
    enter_ = enter_.reset_index(drop=True)
    enter_["inout_site_no"] = enter_["inout_site"].apply(lambda x : find_key(site_dic,x))

    df = enter_.copy()

    df_ = df[["inout_site_no","msgtime","INOUT"]]

    df_in = df_[df_["INOUT"]=="IN"]
    df_out = df_[df_["INOUT"]=="OUT"]
    set_time = pd.date_range(datetime.datetime.strftime(df_["msgtime"].min(),"%Y%m%d"), datetime.datetime.strftime(df_["msgtime"].max(),"%Y%m%d%H")+"0000", freq='h')


    df_in["msgtime"] = df_in["msgtime"].apply(lambda x: datetime.datetime.strptime(str(x)[:13],"%Y-%m-%d %H"))
    df_in = df_in.groupby("msgtime").agg({"inout_site_no":np.size})

    df_in_final = pd.DataFrame(index=set_time)
    df_in_final = pd.merge(df_in_final, df_in, left_index=True, right_index=True, how="left")
    df_in_final.index.freq = "h"
    df_in_final = pd.merge(df_in_final,weather_his.set_index("일시"),left_index=True,right_index=True,how="left")
    df_in_final = df_in_final.fillna(0)
    df_in_final = df_in_final.astype("float64")
    df_in_final = df_in_final.reset_index()
    df_in_final["weekday"] = df_in_final["index"].apply(lambda x : x.weekday())
    df_in_final["holiday"] = df_in_final["index"].apply(alternative_holiday)
    df_in_final["시간"] = df_in_final["index"].apply(lambda x: x.hour)
    df_in_final["년도"] = df_in_final["index"].apply(lambda x: x.year)
    df_in_final["월"] = df_in_final["index"].apply(lambda x: x.month)
    df_in_final["일"] = df_in_final["index"].apply(lambda x: x.day)


    df_out["msgtime"] = df_out["msgtime"].apply(lambda x: datetime.datetime.strptime(str(x)[:13],"%Y-%m-%d %H"))
    df_out = df_out.groupby("msgtime").agg({"inout_site_no":np.size})

    df_out_final = pd.DataFrame(index=set_time)
    df_out_final = pd.merge(df_out_final, df_out, left_index=True, right_index=True, how="left")
    df_out_final.index.freq = "h"
    df_out_final = pd.merge(df_out_final,weather_his.set_index("일시"),left_index=True,right_index=True,how="left")
    df_out_final = df_out_final.fillna(0)
    df_out_final = df_out_final.astype("float64")
    df_out_final = df_out_final.reset_index()

    df_out_final["weekday"] = df_out_final["index"].apply(lambda x : x.weekday())
    df_out_final["holiday"] = df_out_final["index"].apply(alternative_holiday)
    df_out_final["시간"] = df_out_final["index"].apply(lambda x: x.hour)
    df_out_final["년도"] = df_out_final["index"].apply(lambda x: x.year)
    df_out_final["월"] = df_out_final["index"].apply(lambda x: x.month)
    df_out_final["일"] = df_out_final["index"].apply(lambda x: x.day)

    df_in_final["site"] = int(site.split("동")[0])
    df_out_final["site"] = int(site.split("동")[0])

    all_in = pd.concat([all_in,df_in_final])
    all_out = pd.concat([all_out,df_out_final])

    print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), f'Finish Loading and Preprocessing Data - all enter {site}')

all_in = all_in[["index","inout_site_no","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site"]]
all_out = all_out[["index","inout_site_no","기온(°C)","강수량(mm)","풍속(m/s)","습도(%)","적설(cm)","weekday","holiday","시간","년도","월","일","site"]]

all_in.to_csv(data+"all_in.csv",encoding="utf-8-sig",index=False)
all_out.to_csv(data+"all_out.csv",encoding="utf-8-sig",index=False)
