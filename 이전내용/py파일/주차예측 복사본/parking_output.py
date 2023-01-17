from datetime import datetime
from pathlib import Path
import warnings
import argparse
import os

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y%m%d'), help='execute date')
    opt = parser.parse_args()
    return opt

opt = parse_opt()
date = opt.date
#date = '20221228'

warnings.filterwarnings(action='ignore')

def main(opt):
    import parking_input_data
    import parking_park_analysis
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    path = Path.cwd().parent
    raw_data = str(path) + '/raw_data/'
    data = str(path) + '/data/'
    result_data = str(path) + '/result_data/'
    if not os.path.exists(str(path)+'/result_data/'):
        os.makedirs(str(path)+'/result_data/')


    print('!!!!!!!!!!!!!!! Start output.py !!!!!!!!!!!!!!!')
    result_table = parking_park_analysis.result_table
    dataset = parking_input_data.dataset
    predict_dataset =parking_input_data.predict_dataset
    
    ######### 이 부분이 나중에 데이터베이스에 insert하는 부분으로 바뀔 겁니다.
    #dataset.to_csv(data+'dataset.csv', index=False, encoding='utf-8-sig')
    #predict_dataset.to_csv(data+'predict_dataset.csv', index=False, encoding='utf-8-sig')
    result_table.to_csv(result_data+f'parking_08_park_analysis_{date}.csv', index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)