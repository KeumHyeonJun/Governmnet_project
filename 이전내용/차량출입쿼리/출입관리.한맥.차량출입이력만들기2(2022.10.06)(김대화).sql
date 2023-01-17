create table car_in_out_history2
as
select a.system_id
     , a.gvrn_code
     , a.location_id
     , a.car_in_out_key
     , a.car_no
     , a.car_in_out_time as in_time
     , b.car_in_out_time as out_time
     , b.car_stay_minutes
     , a.car_type1
     , a.car_type2
from (
		select * 
		from car_in_out_history a
		where 1=1
		and a.car_in_out_div = 1
	) a left join 
	(
		select * 
		from car_in_out_history a
		where 1=1
		and a.car_in_out_div = 2
	) b on a.car_in_out_key = b.car_in_out_key
where 1=1
union all
select a.system_id
     , a.gvrn_code
     , a.location_id
     , concat('key-', a.car_no, '-out-', a.car_in_out_time) as car_in_out_key
     , a.car_no
     , a.car_in_time  as in_time
     , a.car_in_out_time as out_time
     , a.car_stay_minutes
     , a.car_type1
     , a.car_type2
from car_in_out_history a
where 1=1
and a.car_in_out_div = 2 
and a.car_in_time is null