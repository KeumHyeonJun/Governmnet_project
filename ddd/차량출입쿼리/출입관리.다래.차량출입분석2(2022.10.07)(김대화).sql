select min(car_in_time), max(car_in_time), count(*)
from car_in_out_history2 cioh 
where car_in_time is not null
;

select distinct (car_in_location)
from car_in_out_history2 cioh 
where car_in_time is not null
order by 1
;

select car_type1, count(*)
from car_in_out_history2 cioh 
where car_in_time is not null
group by car_type1
;

-- 다래 : 차량 체류기간 분석
select a.* 
     , round(a.stay_minutes/60/24, 1) as staty_days
from car_in_out_history2 a
where 1=1
order by staty_days desc
;

-- 다래 : 차량 체류시간 상위권 분석
select car_no
     , car_type1
     , count(*) cnt
     , round(max(a.stay_minutes/60/24), 1) max_days
     , round(avg(a.stay_minutes/60/24), 1) avg_days
     , round(min(a.stay_minutes/60/24), 1) min_days
from car_in_out_history2 a
where 1=1
and a.stay_minutes >= 60*24*1
-- and a.car_type1 <> '정기권'
group by car_no, car_type1
order by cnt desc
;

-- 강제출차
select * 
from car_in_out_history2 
where 1=1
and ( car_out_time is null or car_in_time is null)
;

-- 입출 분석
select yyyymmdd as in_date
     , max(weekday) as weekday
     , count(*) as cnt_all
     , sum(case when car_type1 = '정기권' then 1 else 0 end) cnt_정기권
     , sum(case when car_type1 <> '정기권' then 1 else 0 end) cnt_일반
     , sum(case when hh <= '07시' then 1 else 0 end) cnt_07
     , sum(case when hh = '08시' then 1 else 0 end) cnt_08
     , sum(case when hh = '09시' then 1 else 0 end) cnt_09
     , sum(case when hh = '10시' then 1 else 0 end) cnt_10
     , sum(case when hh = '11시' then 1 else 0 end) cnt_11
     , sum(case when hh = '12시' then 1 else 0 end) cnt_12
     , sum(case when hh = '13시' then 1 else 0 end) cnt_13
     , sum(case when hh = '14시' then 1 else 0 end) cnt_14
     , sum(case when hh = '15시' then 1 else 0 end) cnt_15
     , sum(case when hh = '16시' then 1 else 0 end) cnt_16
     , sum(case when hh = '17시' then 1 else 0 end) cnt_17
     , sum(case when hh = '18시' then 1 else 0 end) cnt_18
     , sum(case when hh = '19시' then 1 else 0 end) cnt_19
     , sum(case when hh >= '20시' then 1 else 0 end) cnt_20
from (
			select car_in_location
			     , str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s') as car_in_time     
			     , date_format(str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s'), '%Y년') as yyyy
			     , date_format(str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s'), '%m월') as mm
			     , date_format(str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s'), '%Y-%m월') as yyyymm
			     , date_format(str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s'), '%Y-%m-%d') as yyyymmdd
			     , date_format(str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s'), '%H시') as hh
			     , case weekday(str_to_date(car_in_time, '%Y-%m-%d %H:%i:%s'))
			            when 0 then '월'
			            when 1 then '화'
			            when 2 then '수'
			            when 3 then '목'
			            when 4 then '금'
			            when 5 then '토'
			            when 6 then '일'
			       end as weekday --  0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일      
			     , a.car_type1
			from car_in_out_history2 a
			where 1=1
			and a.car_in_time is not null
		) t 
where 1=1
group by yyyymmdd
order by 1
;
