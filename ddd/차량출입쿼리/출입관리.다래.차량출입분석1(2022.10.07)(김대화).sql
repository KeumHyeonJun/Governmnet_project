-- 다래 차량출입 (입차, 출차 연결)
-- drop table car_in_out_history2;

create table car_in_out_history2
as
select '다래' 							as system_id
     , '05' 							as gvrn_code     
     , a.주차일련번호 						as car_in_out_key
     , a.차량번호  						as car_no     
     , a.장비명   						as car_in_location
     , concat(a.입차일자, ' ', a.입차시각) 	as car_in_time
     , b.장비명   as car_out_location
     , concat(b.출차일자, ' ', b.출차시각) 	as car_out_time     
     , case when b.주차일련번호 is not null 
            then TIMESTAMPDIFF(MINUTE, str_to_date(concat(a.입차일자, ' ', a.입차시각), '%Y-%m-%d %H:%i:%s'), str_to_date(concat(b.출차일자, ' ', b.출차시각), '%Y-%m-%d %H:%i:%s'))
            else null
            end 						as stay_minutes
     , a.출차여부 							as car_out
     , a.입차고객구분 						as car_type1
     , a.차량종류 							as car_type2
     , a.입차구분 							as car_type3
from vw_incarinfo a
     left join vw_outcarinfo b on a.주차일련번호  = b.주차일련번호 
where 1=1
-- and b.주차일련번호 is null
-- and a.차량번호 = '68우2263'
union all
select '다래' 							as system_id
     , '05' 							as gvrn_code     
     , b.주차일련번호 						as car_in_out_key
     , b.차량번호  						as car_no     
     , null   							as car_in_location
     , null 							as car_in_time
     , b.장비명   						as car_out_location
     , concat(b.출차일자, ' ', b.출차시각) 	as car_out_time     
     , null								as stay_minutes	
     , b.출차여부 							as car_out
     , b.출차고객구분 						as car_type1
     , b.차량종류 							as car_type2
     , b.출차구분 							as car_type3
from vw_incarinfo a
     right join vw_outcarinfo b on a.주차일련번호  = b.주차일련번호 
where 1=1
  and a.주차일련번호 is null
;