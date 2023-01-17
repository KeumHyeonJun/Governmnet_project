from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
from pathlib import Path
import pandas as pd
import warnings
import requests
# import datetime ########## from datetime import datetime으로 변경
from datetime import datetime
# import optuna ########## 사용하지 않으므로 삭제
import json
import copy
import os
import parking_input_data
print('!!!!!!!!!!!!!!! Start park_analysis.py !!!!!!!!!!!!!!!')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = Path.cwd().parent
raw_data = str(path) + '/raw_data/'
data = str(path) + '/data/'
result = str(path) + '/result_data/'

warnings.filterwarnings(action='ignore')

# 데이터 로드
print(datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Load Data')
df = parking_input_data.dataset
df = df.astype(float)
df[['연','월','일','시']] = df[['연','월','일','시']].astype(int)

predict_df = parking_input_data.predict_dataset
predict_df=predict_df.astype(float)
predict_df[['연','월','일','시']] = predict_df[['연','월','일','시']].astype(int)

# train, test 나누기
train_data, test_data = train_test_split(df, test_size=0.33, random_state=42)

X_train, y_train = train_data.drop('혼잡도', axis=1), train_data['혼잡도']
X_test, y_test = test_data.drop('혼잡도', axis=1), test_data['혼잡도']

# 모델 적합
print(datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Fit Model')
model = LGBMClassifier(random_state=42) ######## 실행할 때마다 결과가 바뀌면 안 됨 --> random_state 지정
model.fit(X_train, y_train, categorical_feature=['주차장'], eval_set=(X_test,y_test), verbose=1)

# 적합된 모델로 혼잡도 예측
print(datetime.now().strftime('%Y.%m.%d %Hh%Mm%Ss'), 'Predict')
predict_df = predict_df[X_train.columns]


predict = pd.DataFrame(model.predict(predict_df))
output = pd.concat([predict_df, predict], axis= 1)
output = output.rename(columns={0:'혼잡도예측'})
output = output[['연','월','일','시','분','요일','주차장','혼잡도예측']]

# 예측일시, 시간대 추가
output['예측일시'] = output['연'].astype(str) + output['월'].astype(str) + output['일'].astype(str)
output['시간대'] = output['시'].astype(str) + output['분'].astype(str)

# 결과 테이블 만들기
result_table = pd.DataFrame(columns=['등록일시', '주차장명', '예측일시', '시간대', '혼잡도'])
result_table['주차장명'] = output['주차장']
result_table['예측일시'] = output['예측일시']
result_table['시간대'] = output['시간대']
result_table['혼잡도'] = output['혼잡도예측']
result_table['등록일시'] = datetime.now().strftime('%Y%m%d%H%M%S')
result_table = result_table.astype(str)
#result_table.to_csv(result + f'park_analysis.csv', index=False, encoding='utf-8-sig')

