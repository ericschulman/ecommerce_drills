select platform, date, model, manufacturer, price, list_price, rank from prices
where model is not NULL
order by model, manufacturer, date, platform;


WITH summary_stats1 as (
select model, manufacturer, count(*) as obs, count(DISTINCT platform) as sellers,
 avg(price), avg(price*price) - avg(price)*avg(price) as var_price
from prices
where model is not NULL
group by model, manufacturer)

select * from summary_stats1
order by obs DESC;