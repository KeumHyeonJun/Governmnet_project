-- 자량출입이력 만들기 : 한맥
-- drop table car_in_out_history;
create table car_in_out_history
as
select '한맥' 			as system_id
     , '05'				as gvrn_code
     , a.LPRNo   		    as location_id
     , case when a.InOutDiv = 2 and b.InOutDiv = 1 then concat('한맥-', a.carNo, '-in-', b.CarInOutDtime)
            when a.InOutDiv = 1 then concat('한맥-', a.carNo, '-in-', a.CarInOutDtime)
            else null 
            end 		as car_in_out_key
     , a.carNo  		as car_no    
     , a.InOutDiv 		as car_in_out_div
     , a.CarInOutDtime 	as car_in_out_time
     -- , str_to_date(a.CarInOutDtime, '%Y-%m-%d %H:%i') as CarInOutDtime2     
     , b.CarInOutDtime 	as car_in_time
     , case when a.InOutDiv = 2 and b.InOutDiv = 1 then TIMESTAMPDIFF(MINUTE,str_to_date(b.CarInOutDtime, '%Y-%m-%d %H:%i'),str_to_date(a.CarInOutDtime, '%Y-%m-%d %H:%i')) 
            else 0
            end 		as car_stay_minutes
     , a.carType 		as car_type1
     , a.OfficialCar 	as car_type2
from (
		select carType
		     , carNo
		     , OfficialCar
		     , InOutDiv
		     , CarInOutDtime
		     , LPRNo
		     , row_number() over(PARTITION BY CarNo order by carNo, CarInOutDtime) as rowno
		from (
				select '일반차량'          as carType
				     , CarNo            as carNo
				     , ''               as OfficialCar
				     , InOutDiv         as InOutDiv
				     , CarInOutDtime    as CarInOutDtime
				     , convert(LPRNo , char(10)) as LPRNo
				from 일반차량 
				union all 
				select '정기권차량'        as carType
				     , CarNo           as carNo
				     , OfficialCar     as OfficialCar
				     , InOutDiv        as InOutDiv
				     , insDtime        as CarInOutDtime
				     , ''			   as LPRNo
				from 정기권차량
			) t
		where 1=1
		  -- and carno = '01두2608'		
	 ) a left join 
	 (
	 	select carType
		     , carNo
		     , OfficialCar
		     , InOutDiv
		     , CarInOutDtime
		     , LPRNo
		     , row_number() over(PARTITION BY CarNo order by carNo, CarInOutDtime) as rowno
		from (
				select '일반차량'          as carType
				     , CarNo            as carNo
				     , ''               as OfficialCar
				     , InOutDiv         as InOutDiv
				     , CarInOutDtime    as CarInOutDtime
				     , convert(LPRNo , char(10)) as LPRNo
				from 일반차량 
				union all 
				select '정기권차량'        as carType
				     , CarNo           as carNo
				     , OfficialCar     as OfficialCar
				     , InOutDiv        as InOutDiv
				     , insDtime        as CarInOutDtime
				     , ''			   as LPRNo
				from 정기권차량
			) t
		where 1=1
		  -- and carno = '01두2608'		
	 ) b on a.carNo = b.carNo and a.rowno = b.rowno+1
where 1=1
-- order by carNo, CarInOutDtime
;