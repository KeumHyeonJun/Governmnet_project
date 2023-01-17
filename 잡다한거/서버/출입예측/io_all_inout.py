import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
import os
import warnings
from lightgbm import LGBMRegressor
import io_output

print('!!!!!!!!!!!!!!! Start all_inout.py !!!!!!!!!!!!!!!')

os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
data = str(path) + '/data/'
result = str(path) + '/result_data/'
check = str(path) + '/check/'

warnings.filterwarnings(action='ignore')

date = io_output.date

# 데이터 로드
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')

site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-2","2-1"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","종합안내","6-3"],
            "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
            "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-3","복편","17-2","17-1"]}


df_in = pd.read_csv(data+"all_in.csv")
df_out = pd.read_csv(data+"all_out.csv")
new_df_ = pd.read_csv(data+'predict_data.csv')

df_in.loc[df_in[df_in["index"]=="2022-01-01 00:00:00"].index,"weekday"] = 5
df_in.loc[df_in[df_in["index"]=="2022-01-01 00:00:00"].index,"holiday"] = 1
df_in.loc[df_in[df_in["index"]=="2022-01-01 00:00:00"].index,"시간"] = 0
df_in.loc[df_in[df_in["index"]=="2022-01-01 00:00:00"].index,"년도"] = 2022
df_in.loc[df_in[df_in["index"]=="2022-01-01 00:00:00"].index,"월"] = 1
df_in.loc[df_in[df_in["index"]=="2022-01-01 00:00:00"].index,"일"] = 1

df_out.loc[df_out[df_out["index"]=="2022-01-01 00:00:00"].index,"weekday"] = 5
df_out.loc[df_out[df_out["index"]=="2022-01-01 00:00:00"].index,"holiday"] = 1
df_out.loc[df_out[df_out["index"]=="2022-01-01 00:00:00"].index,"시간"] = 0
df_out.loc[df_out[df_out["index"]=="2022-01-01 00:00:00"].index,"년도"] = 2022
df_out.loc[df_out[df_out["index"]=="2022-01-01 00:00:00"].index,"월"] = 1
df_out.loc[df_out[df_out["index"]=="2022-01-01 00:00:00"].index,"일"] = 1

site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-2","2-1"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","종합안내","6-3"],
            "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
            "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-3","복편","17-2","17-1"]}


def lgb_modeling(df):
    df2 = df.copy()
    df2["index"] = df2["index"].astype("datetime64")

    set_time = pd.date_range(datetime.datetime.strftime(df2["index"].min(),"%Y%m%d"), datetime.datetime.strftime(df2["index"].max(),"%Y%m%d%H")+"0000", freq='h')
    df_trend = pd.DataFrame(index=set_time)
    df_trend["trend"] = range(0,len(df_trend))

    trend = df_trend["trend"].max()+1
    df2 = pd.merge(df2.set_index("index"),df_trend,left_index=True,right_index=True,how="left").reset_index()

    # 데이터 전체 기간(일)
    day = int(str(df2["index"].max() - df2["index"].min()).split()[0])+1
    df2[["weekday","site","년도","월","일","시간"]] = df2[["weekday","site","년도","월","일","시간"]].astype(int)

    # train, test 데이터셋 시간 순으로 나열하여 8:2 비율
    train_enter2 = df2[df2["index"] <= df2["index"].max() - relativedelta(days=round(day*0.2))].drop("index",axis=1)
    train_x2 = train_enter2.iloc[:, 1:]
    train_y2 = train_enter2.iloc[:, 0]

    test_enter2 = df2[df2["index"] > df2["index"].max() - relativedelta(days=round(day*0.2))].drop("index",axis=1)
    test_x2 = test_enter2.iloc[:, 1:]
    test_y2 = test_enter2.iloc[:, 0]

    model = LGBMRegressor(random_state=100,n_estimators=200)
    model.fit(train_x2,train_y2,categorical_feature=["weekday","site","년도","월","일","시간"],eval_set=(test_x2,test_y2),verbose=1)

    return model, trend


# 모델 적합
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Fit Model')
model_in, trend_in = lgb_modeling(df_in)
model_out, trend_out = lgb_modeling(df_out)


new_df_["일시"] = new_df_["일시"].astype("datetime64")

test_df = pd.DataFrame()
for site in site_dic.keys():
    site_no = int(site.split("동")[0])
    add_df = new_df_.copy()
    add_df["site"] = site_no
    test_df = pd.concat([test_df,add_df])

test_df.set_index("일시",inplace=True)
df_trend = pd.DataFrame(index=new_df_["일시"])
df_trend["trend"] = range(trend_in, trend_in + len(df_trend))
test_df = pd.merge(test_df,df_trend,left_index=True,right_index=True,how="left").reset_index()


print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Predict')
predict_in = pd.DataFrame({"예측값_in":np.around(model_in.predict(test_df.set_index("일시")))}, index=test_df["일시"])
predict_in[predict_in["예측값_in"]<=0] = 0

predict_out = pd.DataFrame({"예측값_out":np.around(model_out.predict(test_df.set_index("일시")))}, index=test_df["일시"])
predict_out[predict_out["예측값_out"]<=0] = 0

all_predict = pd.concat([predict_in,predict_out],axis=1)
all_predict = pd.concat([all_predict,test_df.set_index("일시")[["site"]]],axis=1)

all_predict.reset_index(inplace=True)
all_predict["예측일시"] = all_predict["일시"].apply(lambda x : datetime.datetime.strftime(x,"%Y%m%d"))
all_predict["시간대"] = all_predict["일시"].apply(lambda x : datetime.datetime.strftime(x,"%H"))
all_predict["등록일시"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
all_predict = all_predict.drop("일시",axis=1)

all_predict = all_predict[["등록일시","site","예측일시","시간대","예측값_in","예측값_out"]]
all_predict = all_predict.rename(columns = {"site":"위치","예측값_in":"진입인원수","예측값_out":"진출인원수"})
all_predict.sort_values(["위치","시간대"],inplace=True)

weekday = datetime.datetime.strptime(date,"%Y%m%d").weekday()
df_in_weekday = df_in[df_in["weekday"]==weekday]
df_in_weekday = df_in_weekday.groupby(["site","시간"]).agg({"inout_site_no":np.mean}).rename(columns={"inout_site_no":"평균진입인원수"})
df_out_weekday = df_out[df_out["weekday"]==weekday]
df_out_weekday = df_out_weekday.groupby(["site","시간"]).agg({"inout_site_no":np.mean}).rename(columns={"inout_site_no":"평균진출인원수"})

df_mean = round(pd.concat([df_in_weekday,df_out_weekday],axis=1))
df_mean.reset_index(inplace=True)
df_mean["시간"] = df_mean["시간"].astype("int64")
df_mean["시간"] = df_mean["시간"].apply(lambda x : str(x).zfill(2))

all_predict = pd.merge(all_predict,df_mean,left_on=["위치","시간대"],right_on=["site","시간"],how="inner").drop(["site","시간"],axis=1)
all_predict = all_predict.astype(str)
# all_predict



# 데이터 로드
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
visit = pd.read_csv(data+"visit_ratio.csv")
gong = pd.read_csv(data+"emp_ratio.csv")
# 선택한 날짜 기준 한달간의 공무원, 방문객의 평균 출입 비율 산출
emp_visit = pd.DataFrame(visit["inout_site_no"].value_counts() / gong["inout_site_no"].value_counts())
emp_visit.reset_index(inplace=True)
emp_visit["등록일시"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
emp_visit.rename(columns={"index":"위치","inout_site_no":"비율"},inplace=True)
emp_visit = emp_visit[["등록일시","위치","비율"]]
enp_visit = emp_visit.astype(str)
# emp_visit

# all_predict.to_csv(result+"ent_analysis.csv",index=False,encoding="utf-8-sig")
# emp_visit.to_csv(result+"emp_visit_ratio.csv",index=False,encoding="utf-8-sig")