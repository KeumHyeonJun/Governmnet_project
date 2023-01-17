-- 대웅 차량 입출차 정보 (16동, 17동)
select *
from (
select a.SystemNo								-- 시스템번호
     , a.ParkNo									-- 주차장 번호
     , a.MainUnitNo as in_mainunitno 			-- 입고 Unit
     , b.UnitName as in_mainunitname			-- 입고 Unit
     , a.ProcDate as in_date					-- 입고 일자
     , a.ProcTime as in_time					-- 입고 시간
     , a.InCarNo as in_carno					-- 차량 번호
     , z.ExitMainUnitNo as out_mainunitno		-- 출고 Unit
     , z.ExitMainUnitname as out_mainunitname	-- 출고 unit
     , z.out_date								-- 출고 일자
     , z.out_time								-- 출고 시간
     , a.CarType 								-- 차량 유형
from PS500 a -- 차량입고
left join PS070 b on a.MainUnitNo = b.MainUnitNo
left join (
    -- 입고정보 있는 차량 출고 
	select a.SystemNo  						-- 시스템번호
	    , a.ParkNo  						-- 주차장 번호
	    , a.ExitMainUnitNo 					-- 출고 unit
	    , b.UnitName as ExitMainUnitname 	-- 출고 unit 명
	    , a.ProcDate as out_date 			-- 출고 일자
	    , a.ProcTime as out_time 			-- 출고 시간
	    , a.InCarNo 						-- 차량번호
	    , a.MainUnitNo as in_mainunitno		-- 입고 unit
	    , c.UnitName as in_mainunitname		-- 입고 unit 명
	    , a.InDate as in_date				-- 입고 일자
	    , a.InTime as in_time				-- 입고 시간
	from PS510 a
	left join PS070 b on a.ExitMainUnitNo = b.MainUnitNo 
	left join PS070 c on a.MainUnitNo = c.MainUnitNo 
	where 1=1
	and ifnull(a.MainUnitNo, '') <> ''
	) z on a.SystemNo = z.SystemNo
	   and a.ParkNo = z.ParkNo
	   and a.MainUnitNo = z.in_mainunitno
	   and a.ProcDate = z.in_date
	   and a.ProcTime = z.In_Time
	   and a.InCarNo = z.InCarNo
union ALL 
-- 입고정보 없는 출고차량
select a.SystemNo 							-- 시스템 번호
    , a.ParkNo 								-- 주차장 번호
    , '' as in_mainunitno					-- 입고 Unit
    , '' as in_mainunitname					-- 입고 Unit 명
    , '' as in_date							-- 입고 일자
    , '' as in_time							-- 입고 시간
    , a.InCarNo as in_carno					-- 차량 번호
    , a.ExitMainUnitNo  as out_mainunitno 	-- 출고 unit
    , b.UnitName as out_mainunitname		-- 출고 Uni
    , a.ProcDate as out_date				-- 출고 일자				-- 
    , a.ProcTime as out_time				-- 출고 시간
    , a.CarType 							-- 차량 유형
from PS510 a
left join PS070 b on a.ExitMainUnitNo = b.MainUnitNo 
where ifnull(a.MainUnitNo, '') = ''
) t 
where 1=1
-- and t.in_carno = '92모1769'
and t.in_carno <> ''
order by in_carno
       , case when in_date is not null then in_date || in_time else out_date || out_time end