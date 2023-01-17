import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
import os
import warnings
import dev_output

print('!!!!!!!!!!!!!!! Start material_analysis.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
raw_data = str(path) + '/raw_data/'
data = str(path) + '/data/'
result = str(path) + '/result_data/'

warnings.filterwarnings(action='ignore')

date = dev_output.date

# 데이터 Load
print(datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
import query

fmsb06 = query.FMSB06
fmsb07 = query.FMSB07
fmsb30 = query.FMSB30
fmsa11 = query.FMSA11
fmsx04 = query.FMSX04
fmsx05_ = pd.read_csv(data+"FMSX05_ver2.csv",dtype={"fac_cd":str})

기계 = pd.read_csv(data + 'mec_finish.csv')
통신 = pd.read_csv(data +'tel_finish.csv')
방재 = pd.read_csv(data +'prevent_finish.csv')
승강기 = pd.read_csv(data +'elevator_finish.csv')
전기 = pd.read_csv(data +'electric_finish.csv')





# 자재 재고량 통합
fmsb30_ = fmsb30.copy()
fmsb30_ = fmsb30_[["mat_cd","mat_nm","mat_type","inv_qty"]]
fmsb30_["inv_qty"] = fmsb30_["inv_qty"].astype(int)
fmsb30_ = fmsb30_.groupby(["mat_cd","mat_nm","mat_type"]).sum().reset_index()
# mat_type이 " 하나가 추가되어 다르게 읽히는 경우 존재
fmsb30_.drop_duplicates(["mat_cd","mat_nm"],inplace=True)



# 월평균 출고량
# 월평균 출고량 column 생성
fmsb07_ = fmsb07.copy()
fmsb07_ = fmsb07_[["job_cd","mat_cd","outw_qty","outw_day","mat_nm","mat_type","input_sysdt","wh_cd"]]
fmsb07_["outw_qty"] = fmsb07_["outw_qty"].astype(int)
fmsb07_["outw_day"] = fmsb07_["outw_day"].astype("datetime64")
# 선택한 날짜 이전 1년의 데이터만 사용
fmsb07_ = fmsb07_[(fmsb07_["outw_day"] >= datetime.strptime(date,"%Y%m%d") - relativedelta(years=1)) & (fmsb07_["outw_day"] < datetime.strptime(date,"%Y%m%d"))]
# 선택한 columns 모두 똑같으면 중복데이터로 가정
fmsb07_.drop_duplicates(["job_cd","mat_cd","outw_qty","outw_day","mat_nm","mat_type","input_sysdt","wh_cd"],inplace=True)

for cd in fmsb07_["mat_cd"].unique():
    for typ in fmsb07_[fmsb07_["mat_cd"]==cd]["mat_type"].unique():
        # 자재코드와 자재유형이 같은 자재의 출고량 합계
        outw_sum = fmsb07_[(fmsb07_["mat_cd"]==cd) & (fmsb07_["mat_type"]==typ)]["outw_qty"].sum()
        # 데이터 기간 산출(월 단위)
        delta = relativedelta(fmsb07_["outw_day"].max(), fmsb07_["outw_day"].min())
        # 자재코드와 자재 유형이 같은 자재의 월평균 출고량 산출
        fmsb07_.loc[(fmsb07_["mat_cd"]==cd) & (fmsb07_["mat_type"]==typ),"outw_mean"] = round(outw_sum / (12 * delta.years + delta.months))
# 필요한 columns만 추출
fmsb07_ = fmsb07_[["job_cd","mat_cd","mat_nm","mat_type","outw_mean"]]
# 작업코드, 자재코드, 자재유형이 중복된 데이터는 삭제 --> 월평균 출고량이 같기 때문에 하나의 데이터만 있어도 충분
fmsb07_.drop_duplicates(["job_cd","mat_cd","mat_type"],inplace=True)



# 월평균 입고량
# 월평균 입고량 column 생성
fmsb06_ = fmsb06.copy()
fmsb06_ = fmsb06_[["mat_cd","inw_qty","inw_day","mat_nm","mat_type","input_sysdt","wh_cd"]]
fmsb06_["inw_qty"] = fmsb06_["inw_qty"].astype(int)
fmsb06_["inw_day"] = fmsb06_["inw_day"].astype("datetime64")
# 선택한 날짜 이전 1년의 데이터만 사용
fmsb06_ = fmsb06_[(fmsb06_["inw_day"] >= datetime.strptime(date,"%Y%m%d") - relativedelta(years=1)) & (fmsb06_["inw_day"] < datetime.strptime(date,"%Y%m%d"))]
# 선택한 columns 모두 똑같으면 중복데이터로 가정
fmsb06_.drop_duplicates(["mat_cd","inw_qty","inw_day","mat_nm","mat_type","input_sysdt","wh_cd"],inplace=True)

for cd in fmsb06_["mat_cd"].unique():
    for typ in fmsb06_[fmsb06_["mat_cd"]==cd]["mat_type"].unique():
        # 자재코드와 자재유형이 같은 자재의 입고량 합계
        inw_sum = fmsb06_[(fmsb06_["mat_cd"]==cd) & (fmsb06_["mat_type"]==typ)]["inw_qty"].sum()
        # 데이터 기간 산출(월 단위)
        delta = relativedelta(fmsb06_["inw_day"].max(), fmsb06_["inw_day"].min())
        # 자재코드와 자재 유형이 같은 자재의 월평균 입고량 산출
        fmsb06_.loc[(fmsb06_["mat_cd"]==cd) & (fmsb06_["mat_type"]==typ),"inw_mean"] = round(inw_sum / (12 * delta.years + delta.months))
# 필요한 columns만 추출
fmsb06_ = fmsb06_[["mat_cd","mat_nm","mat_type","inw_mean"]]
# 자재코드, 자재유형이 중복된 데이터는 삭제 --> 월평균 입고량이 같기 때문에 하나의 데이터만 있어도 충분
fmsb06_.drop_duplicates(["mat_cd","mat_type"],inplace=True)


# 재고, 출고, 입고 join
# mat_type이 서로 다른 것이 존재하지만 표현의 차이일 뿐 같은 의미이기 때문에 fmsb30_의 mat_type으로 통일
fmsb0730 = pd.merge(fmsb30_,fmsb07_[["job_cd","mat_cd","mat_type","outw_mean"]],on=["mat_cd","mat_type"],how="left")
# mat_cd, mat_nm, mat_type이 전부 같더라도 job_cd가 다름 --> 결국 중요한 것은 job_cd가 겹치지 않는 것!!
final = pd.merge(fmsb0730,fmsb06_[["mat_cd","mat_type","inw_mean"]],on=["mat_cd","mat_type"],how="left")


final = final.loc[final["job_cd"].dropna().index,].fillna(0)
final = final[["job_cd","mat_cd","mat_nm","mat_type","inv_qty","outw_mean","inw_mean"]]


# job_fac의 장비 분류 코드를 활용해 장비 분류명 삽입
# class_cd_4 --> Lv4
job_fac = pd.merge(fmsa11[["job_cd","fac_cd"]], fmsx05_[["class_nm_1","class_nm_2","class_nm_3","class_nm_4","fac_cd","class_cd_4"]], on="fac_cd",how="left")

fmsx04 = fmsx04.drop(index=fmsx04[fmsx04["class_cd"]=="ROOT"].index,axis=0)
fmsx04["class_cd"] = fmsx04["class_cd"].astype("int64")

# Lv4 기준이기 때문에 fac_cd가 다르더라도 Lv4가 같아서 하나의 장비 --> 중복 데이터 취급
fac = pd.merge(job_fac[["job_cd","class_nm_1","class_nm_2","class_nm_3","class_nm_4","class_cd_4"]], fmsx04[["class_cd","class_nm"]], left_on="class_cd_4",right_on="class_cd",how="left").astype(str)
fac.drop_duplicates(inplace=True)




def make_df(df):
    df_ = df.copy()
    df_ = df_[["그룹정의","Lv1","Lv2","Lv3","Lv4"]]
    # 장비 계층을 활용해 그룹 정의한 테이블과 join
    fac_df = pd.merge(df_,fac[["job_cd","class_nm_1","class_nm_2","class_nm_3","class_nm_4"]],left_on=["Lv1","Lv2","Lv3","Lv4"],right_on=["class_nm_1","class_nm_2","class_nm_3","class_nm_4"],how="left")
    # join한 테이블에 자재에 대한 재고, 출고, 입고 테이블 join
    final_fac_df = pd.merge(fac_df,final[["job_cd","mat_nm","mat_type","inv_qty","outw_mean","inw_mean"]],on="job_cd",how="left")

    index_na = final_fac_df[final_fac_df["mat_nm"].isna()].index
    final_df = final_fac_df.drop(index_na,axis=0)

    final_df = final_df.fillna(0)
    final_df[["inv_qty","outw_mean","inw_mean"]] = final_df[["inv_qty","outw_mean","inw_mean"]].astype("int64")
    final_df = final_df[["그룹정의","mat_nm","mat_type","inv_qty","outw_mean","inw_mean"]]
    final_df = final_df.rename(columns={"그룹정의":"장비분류","mat_nm":"자재명","mat_type":"자재유형","inv_qty":"재고량","outw_mean":"월평균출고량","inw_mean":"월평균입고량"})
    df_final = pd.DataFrame()
    for i in final_df["장비분류"].unique():
        a = final_df[final_df["장비분류"]==i]
        # 장비에 사용된 자재가 3개 미만이라면 전체 자재 보여줌
        if len(a[["자재명","자재유형"]].value_counts()) < 3:
            for i in range(len(a[["자재명","자재유형"]].value_counts())):
                df_final = pd.concat([df_final,a[(a["자재명"]==a[["자재명","자재유형"]].value_counts().index[i][0]) & (a["자재유형"]==a[["자재명","자재유형"]].value_counts().index[i][1])].drop_duplicates()],axis=0)
        else:
            # 장비에 사용된 자재가 3개 이상이라면 출고 숫자 상위 3개 자재만 보여줌
            b = a[["자재명","자재유형"]].value_counts().head(3)
            con1_nm = b.index[0][0]
            con1_type = b.index[0][1]
            con2_nm = b.index[1][0]
            con2_type = b.index[1][1]
            con3_nm = b.index[2][0]
            con3_type = b.index[2][1]
            a1 = a[(a["자재명"]==con1_nm) & (a["자재유형"]==con1_type)].drop_duplicates()
            a2 = pd.concat([a1,a[(a["자재명"]==con2_nm) & (a["자재유형"]==con2_type)].drop_duplicates()],axis=0)
            a3 = pd.concat([a2,a[(a["자재명"]==con3_nm) & (a["자재유형"]==con3_type)].drop_duplicates()],axis=0)
            df_final = pd.concat([df_final,a3],axis=0)
    return df_final



result = pd.concat([make_df(기계),make_df(전기),make_df(방재),make_df(승강기),make_df(통신)])
result['등록일시'] = datetime.now().strftime('%Y%m%d%H%M%S')
result = result[["등록일시","장비분류","자재명","자재유형","재고량","월평균출고량","월평균입고량"]]
result = result.astype(str)
result_material_analysis = result
print(datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Finish material analysis')

# result.to_csv(result_data+ '자재재고결과.csv',index = False , encoding='utf-8-sig')