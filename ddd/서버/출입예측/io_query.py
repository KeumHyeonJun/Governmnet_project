query1 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "1동%" OR reader_nm LIKE "1-A동%" OR reader_nm LIKE "1-B동%" OR reader_nm LIKE "1-C동%")
'''

query2 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "2동%" OR reader_nm LIKE "2-1동%" OR reader_nm LIKE "2-2동%")
'''

query3 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "3동%");
'''

query4 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "4동%" OR reader_nm LIKE "4-1동%" OR reader_nm LIKE "4-2동%")
'''

query5 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "5동%" OR reader_nm LIKE "5-1동%" OR reader_nm LIKE "5-2동%" OR reader_nm LIKE "5-3동%");
'''

query6 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "6동%" OR reader_nm LIKE "6-1동%" OR reader_nm LIKE "6-2동%" OR reader_nm LIKE "6-3동%" OR reader_nm LIKE "종합안내동%");
'''

query7 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "7-1동%" OR reader_nm LIKE "7-2동%")
'''

query8 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "8동%")
'''

query9 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "9동%");
'''

query10 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "10동%");
'''

query11 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "11동%" OR reader_nm LIKE "11-1동%")
'''

query12 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "12-3동%")
'''

query13 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "13동%" OR reader_nm LIKE "13-1동%" OR reader_nm LIKE "13-2동%")
'''

query14 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "14-3동%" OR reader_nm LIKE "14-1동%" OR reader_nm LIKE "14-2동%")
'''

query15 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "15동%" OR reader_nm LIKE "15-1동%" OR reader_nm LIKE "15-2동%")
'''

query16 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "16동%" OR reader_nm LIKE "16-A동%" OR reader_nm LIKE "16-B동%" OR reader_nm LIKE "국세청%")
'''

query17 = '''
SELECT reader_nm, msgtime
FROM SVC.SHINHWA_TBL_HIST_ACCESS
WHERE reader_nm LIKE "%스피드%" AND event_msg = "Grant access" 
	and p_msgtime between from_timestamp(DATE_SUB(NOW(), INTERVAL 6 MONTH), 'yyyyMMdd') and from_timestamp(now(), 'yyyyMMdd')
	AND (reader_nm LIKE "17동%" OR reader_nm LIKE "17-1동%" OR reader_nm LIKE "17-2동%" OR reader_nm LIKE "17-3%" OR reader_nm LIKE "복편%")
'''

query_dic = {"1동":query1, "2동": query2,"3동":query3, "4동":query4, "5동":query5, "6동":query6, "7동":query7, "8동":query8, "9동":query9,\
    "10동":query10, "11동":query11, "12동":query12, "13동":query13, "14동":query14, "15동":query15, "16동":query16, "17동":query17}