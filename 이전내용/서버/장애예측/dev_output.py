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
# date = '20221213'

warnings.filterwarnings(action='ignore')


def main(opt):
	import dev_input_data
	import dev_material_analysis
	import dev_time_analysis
	import dev_equipment_analysis
	
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	path = Path.cwd().parent
	raw_data = str(path) + '/raw_data/'
	data = str(path) + '/data/'
	result_data = str(path) + '/result_data/'
	if not os.path.exists(str(path) + '/result_data/'):
		os.makedirs(str(path) + '/result_data/')
	
	print('!!!!!!!!!!!!!!! Start output.py !!!!!!!!!!!!!!!')
	material_table = dev_material_analysis.result
	time_table = dev_time_analysis.final
	equipment_table = dev_equipment_analysis.output_data
	######### 이 부분이 나중에 데이터베이스에 insert하는 부분으로 바뀔 겁니다.
	dev_material_analysis.result_material_analysis.to_csv(result_data + f'dev_11_material_analysis_{date}.csv', index=False, encoding='utf-8-sig')
	dev_time_analysis.result_time_alalysis.to_csv(result_data + f'dev_10_time_analysis_{date}.csv', index=False, encoding='utf-8-sig')
	dev_equipment_analysis.result_equipment_analysis.to_csv(result_data + f'dev_09_equipment_analysis_{date}.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
	opt = parse_opt()
	main(opt)