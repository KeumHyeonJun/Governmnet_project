import pandas as pd
import datetime
import numpy as np
from lightgbm import LGBMRegressor
from dateutil.relativedelta import relativedelta
from pathlib import Path
import os
import warnings
import io_output

print('!!!!!!!!!!!!!!! Start visit_inout.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
data = str(path) + '/data/'
check = str(path) + '/check/'
result = str(path) + '/result_data/'

warnings.filterwarnings(action="ignore")

date = io_output.date

start = datetime.datetime.strftime(datetime.datetime.strptime(date,"%Y%m%d")-relativedelta(years=1),"%Y%m%d")
end = datetime.datetime.strftime(datetime.datetime.strptime(date,"%Y%m%d")-relativedelta(days=1),"%Y%m%d")
site_dic = {"1동":["1","1-A","1-B","1-C"], "2동":["2","2-2","2-1"], "3동":"3", "4동":["4","4-1","4-2"], "5동":["5","5-1","5-2","5-3"],"6동":["6","6-1","6-2","종합안내","6-3"],
        "7동":["7-1","7-2"], "8동":"8", "9동":"9", "10동":"10", "11동":["11","11-1"], "12동":"12-3", "13동":["13","13-1","13-2"], "14동":["14-1","14-2","14-3"],
        "15동":["15","15-1","15-2"], "16동":["16","16-A","16-B","국세청"], "17동":["17","17-3","복편","17-2","17-1"]}

#### Data Load
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - visit_comarison')

df_in = pd.read_csv(data+"visit_in.csv")
df_out = pd.read_csv(data+"visit_out.csv")
new_df = pd.read_csv(data+'predict_data.csv')

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

def make_inout_max(df_in, df_out):
    df_in["index"] = df_in["index"].astype("datetime64")
    df_out["index"] = df_out["index"].astype("datetime64")
    # 선택한 날짜 기준 한달 간의 출입인원 max값 산출
    df_in_ = df_in[(df_in["index"] >= (datetime.datetime.strptime(date,"%Y%m%d") - relativedelta(months=1))) & (df_in["index"] < datetime.datetime.strptime(date,"%Y%m%d"))]
    df_out_ = df_out[(df_out["index"] >= (datetime.datetime.strptime(date,"%Y%m%d") - relativedelta(months=1))) & (df_out["index"] < datetime.datetime.strptime(date,"%Y%m%d"))]
    in_grp = df_in_.groupby(["년도","월","일","site"]).agg({"inout_site_no":np.sum}).reset_index()
    out_grp = df_out_.groupby(["년도","월","일","site"]).agg({"inout_site_no":np.sum}).reset_index()

    max_inout = pd.DataFrame(columns=["in","out"],index = site_dic.keys())

    for site in max_inout.index:
        max_inout.loc[site,"in"] = in_grp[in_grp["site"]==int(site.split("동")[0])]["inout_site_no"].max()
        max_inout.loc[site,"out"] = out_grp[out_grp["site"]==int(site.split("동")[0])]["inout_site_no"].max()

    return max_inout


#### 모델 적합
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Fit Model - visit_comparison')

model_in, trend_in = lgb_modeling(df_in)
model_out, trend_out = lgb_modeling(df_out)
max_inout = make_inout_max(df_in,df_out)

# 예측 데이터셋
new_df_ = new_df.copy()
new_df_["일시"] = new_df_["일시"].astype("datetime64")

final_df = pd.DataFrame(index=["1동","2동","3동","4동","5동","6동","7동","8동","9동","10동","11동","12동","13동","14동","15동","16동"],columns=["진입인원비율","진출인원비율"])

# 예측데이터셋에 동 칼럼 추가
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

#### 적합시킨 모델로 예측
print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Predict Model - visit_comparison')
# IN/OUT 예측값 산출
predict_in = pd.DataFrame({"예측값_in":np.around(model_in.predict(test_df.drop("일시",axis=1)))}, index=test_df["일시"])
predict_in[predict_in["예측값_in"]<=0] = 0

predict_out = pd.DataFrame({"예측값_out":np.around(model_out.predict(test_df.drop("일시",axis=1)))}, index=test_df["일시"])
predict_out[predict_out["예측값_out"]<=0] = 0

predict_final = pd.concat([predict_in,predict_out],axis=1)
predict_final = pd.concat([predict_final,test_df[["site","일시"]].set_index("일시")],axis=1).reset_index().sort_values(["site","일시"])

days = (len(predict_final)/17)/24
# 동별 출입 인원을 한달 간 max값으로 나누어 비율 산출
for site in final_df.index:
    final_df.loc[site,"진입인원비율"] = (predict_final[predict_final["site"]==int(site.split("동")[0])]["예측값_in"].sum() / days) / max_inout.loc[site,"in"]
    final_df.loc[site,"진출인원비율"] = (predict_final[predict_final["site"]==int(site.split("동")[0])]["예측값_out"].sum() / days) / max_inout.loc[site,"out"]

final_df.reset_index(inplace=True)
final_df.rename(columns={"index":"위치"},inplace=True)
final_df["등록일시"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
final_df = final_df[["등록일시","위치","진입인원비율","진출인원비율"]]
final_df = final_df.astype(str)
# final_df



print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data - visit_ratio')

visit_in = pd.read_csv(data+"visit_company_in.csv")
visit_out = pd.read_csv(data+"visit_company_out.csv")
company_label = pd.read_csv(data+"company_label.csv")
new_df = pd.read_csv(data+'predict_data.csv')


print(datetime.datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Fit Model - visit_ratio')

def lgb_modeling_ratio(df):
    df2 = df.copy()
    df2["index"] = df2["index"].astype("datetime64")
    
    set_time = pd.date_range(datetime.datetime.strftime(df2["index"].min(),"%Y%m%d"), datetime.datetime.strftime(df2["index"].max(),"%Y%m%d%H")+"0000", freq='h')
    df_trend = pd.DataFrame(index=set_time)
    df_trend["trend"] = range(0,len(df_trend))
    trend = df_trend["trend"].max()+1

    df2 = pd.merge(df2.set_index("index"),df_trend,left_index=True,right_index=True,how="left").reset_index()

    day = int(str(df2["index"].max() - df2["index"].min()).split()[0])+1

    train_enter2 = df2[df2["index"] <= df2["index"].max() - relativedelta(days=round(day*0.2))].set_index("index")
    train_x2 = train_enter2.iloc[:, 1:]
    train_y2 = train_enter2.iloc[:, 0]

    test_enter2 = df2[df2["index"] > df2["index"].max() - relativedelta(days=round(day*0.2))].set_index("index")
    test_x2 = test_enter2.iloc[:, 1:]
    test_y2 = test_enter2.iloc[:, 0]

    model = LGBMRegressor(random_state=100)
    model.fit(train_x2,train_y2,categorical_feature=["weekday","site","년도","월","일","시간","label"],eval_set=(test_x2,test_y2),verbose=1)

    return model,trend 


visit_in_ = visit_in.drop("company",axis=1)
visit_out_ = visit_out.drop("company",axis=1)

# 모델 적합 및 예측값 산출
model_in, trend_in = lgb_modeling_ratio(visit_in_)
model_out, trend_out = lgb_modeling_ratio(visit_out_)

new_df1 = new_df.copy()
new_df1["일시"] = new_df1["일시"].astype("datetime64")

new_df_ = pd.DataFrame()
for site in company_label["site"].unique():
    for label in company_label[company_label["site"]==site]["label"].unique():
        new = new_df1.copy()
        new["site"] = site
        new["label"] = label
        new_df_ = pd.concat([new_df_,new])

df_trend = pd.DataFrame(index=new_df_["일시"].unique())
df_trend["trend"] = range(trend_in, trend_in + len(df_trend))
test_df = pd.merge(new_df_.set_index("일시"),df_trend,left_index=True,right_index=True,how="left")

final_df_in = pd.DataFrame({"예측값":np.around(model_in.predict(test_df))})
final_df_in[final_df_in <= 0] = 0
final_df_in["site"] = test_df['site'].to_list()
final_df_in["label"] = test_df['label'].to_list()
final_df_in["일시"] = test_df.index

final_df_out = pd.DataFrame({"예측값":np.around(model_out.predict(test_df))})
final_df_out[final_df_out <= 0] = 0
final_df_out["site"] = test_df['site'].to_list()
final_df_out["label"] = test_df['label'].to_list()
final_df_out["일시"] = test_df.index

# visit_in_ 테이블에 visit_out_ 테이블 삽입
final_df_in = final_df_in.rename(columns=({"site":"위치","예측값":"진입인원수"}))
final_df_out = final_df_out.rename(columns=({"예측값":"진출인원수"}))

final_df_in["등록일시"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
final_df_in["예측일시"] = final_df_in["일시"].apply(lambda x :datetime.datetime.strftime(x,"%Y%m%d"))
final_df_in["시간대"] = final_df_in["일시"].apply(lambda x :datetime.datetime.strftime(x,"%H"))

for company in final_df_in["label"].unique():
    final_df_in.loc[final_df_in["label"]==company,"부서"] = company_label[company_label["label"]==company]["company"].iloc[0]

visit_inout_ = pd.concat([final_df_in,final_df_out["진출인원수"]],axis=1)

final_df_ = visit_inout_.copy()

# 날짜, 위치 별 인원 수의 합계를 구한 후 각각의 값으로 나누어 부서별, 시간별, 동별 방문객 예상 출입 비율 산출
for ind in final_df_["일시"].unique():
    for site in final_df_["위치"].unique():
        v_sum_in = final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site),"진입인원수"].sum()
        v_sum_out = final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site),"진출인원수"].sum()
        final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site),"진입인원수"] = final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site),"진입인원수"]/v_sum_in
        final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site),"진출인원수"] = final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site),"진출인원수"]/v_sum_out

final_df_ = final_df_.fillna(0)
final_df_.rename(columns={"진입인원수":"진입인원비율","진출인원수":"진출인원비율"},inplace=True)
# predict_final -> 동별, 시간별 방문객 예상 출입 인원 수
predict_final.reset_index(inplace=True)
visit_inout = visit_inout_.copy()
# 부서별, 동별, 시간별 방문객 예상 출입 비율에서 동별, 시간별 방문객 예상 출입 인원 수를 곱하여 부서별 예상 출입 인원 수 산출
for ind in final_df_["일시"].unique():
    for site in final_df_["위치"].unique():
        for com in final_df_[final_df_["위치"]==site]["부서"].unique():
            ratio_in = final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site) & (final_df_["부서"]==com),"진입인원비율"].iloc[0]
            ratio_out = final_df_.loc[(final_df_["일시"]==ind) & (final_df_["위치"]==site) & (final_df_["부서"]==com),"진출인원비율"].iloc[0]
            value_in = predict_final.loc[(predict_final["일시"]==ind) & (predict_final["site"]==site),"예측값_in"].iloc[0]
            value_out = predict_final.loc[(predict_final["일시"]==ind) & (predict_final["site"]==site),"예측값_out"].iloc[0]

            visit_inout.loc[(visit_inout["일시"]==ind) & (visit_inout["위치"]==site) & (visit_inout["부서"]==com),"진입인원수"] = round(ratio_in * value_in)
            visit_inout.loc[(visit_inout["일시"]==ind) & (visit_inout["위치"]==site) & (visit_inout["부서"]==com),"진출인원수"] = round(ratio_out * value_out)
visit_inout.rename(columns={"label":"부서코드"},inplace=True)
visit_inout = visit_inout[["등록일시","위치","부서","부서코드","예측일시","시간대","진입인원수","진출인원수"]]
visit_inout.sort_values(["부서코드","시간대"],inplace=True)
visit_inout = visit_inout.astype(str)

print("!!!!!!!!!!!!!!!finish!!!!!!!!!!!!!!!!!!!!")
#
# visit_inout.to_csv(result+"visitor_analysis.csv",index=False,encoding="utf-8-sig")
# final_df.to_csv(result+"visitor_max_com.csv",index=False,encoding="utf-8-sig")