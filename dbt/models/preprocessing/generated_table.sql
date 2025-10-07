{{
  config(
    materialized = 'table',
    )
}}
select 
    _date
  , _value
from unnest(generate_date_array(current_date-100, current_date, interval 1 day)) _date
cross join unnest(generate_array(1, 100, 1)) _value

union all

select 
    current_date _date
  , _value
from unnest(generate_array(1, 100, 1)) _value