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
# date ='20221228'

warnings.filterwarnings(action='ignore')

def main(opt):
    import io_input_data
    import io_visit_time
    import io_visit_inout
    import io_all_inout
    import io_ent_night
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    path = Path.cwd().parent
    result_data = str(path) + '/result_data/'
    if not os.path.exists(str(path)+'/result_data/'):
        os.makedirs(str(path)+'/result_data/')


    print('!!!!!!!!!!!!!!! Start output.py !!!!!!!!!!!!!!!')
    iqr_df = io_visit_time.iqr_df
    visit_inout_ratio = io_visit_inout.visit_inout
    visit_max_com = io_visit_inout.final_df
    all_ent = io_all_inout.all_predict
    emp_visit = io_all_inout.emp_visit
    night_hour = io_ent_night.night_hour
    night_door = io_ent_night.night_door

    iqr_df.to_csv(result_data+f"io_01_visit_time_{date}.csv",index=False,encoding="utf-8-sig")
    all_ent.to_csv(result_data+f"io_02_ent_analysis_{date}.csv",index=False,encoding="utf-8-sig")
    visit_inout_ratio.to_csv(result_data+f"io_03_visitor_analysis_{date}.csv",index=False,encoding="utf-8-sig")
    visit_max_com.to_csv(result_data+f"io_04_visitor_max_com_{date}.csv",index=False,encoding="utf-8-sig")
    emp_visit.to_csv(result_data+f"io_05_emp_visit_ratio_{date}.csv",index=False,encoding="utf-8-sig")
    night_hour.to_csv(result_data+f"io_06_night_hour_{date}.csv",index=False,encoding="utf-8-sig")
    night_door.to_csv(result_data+f"io_07_night_door_{date}.csv",index=False,encoding="utf-8-sig")


if __name__ == '__main__':
    opt = parse_opt()
    main(opt)