-- 한맥 : 차량 체류기간 분석
select *
    , round(car_stay_minutes/60/24, 1) as stay_days
from car_in_out_history2
where 1=1
-- and in_time is null
-- and car_no = '22무9328'
and car_stay_minutes > 1440
order by stay_days desc
;

-- 한맥 : 차량 체류시간 상위권 분석
select car_no, car_type1
     , count(*) cnt
     , round(max(a.car_stay_minutes/60/24), 1) max_days
     , round(avg(a.car_stay_minutes/60/24), 1) avg_days
     , round(min(a.car_stay_minutes/60/24), 1) min_days
from car_in_out_history2 a
where 1=1
and a.car_stay_minutes >= 60*24*4
-- and a.car_type1 <> '정기권'
-- and a.car_no = '22무9328'
group by a.car_no, car_type1
order by max_days desc
;


select min(in_time), max(in_time), count(*)
from car_in_out_history2 cioh 
where in_time is not null
;

select distinct (location_id)
from car_in_out_history2 cioh 
where in_time is not null
;

select car_type2, count(*)
from car_in_out_history2 cioh 
where in_time is not null
group by car_type2 
;



