{{
  config(
    materialized = 'view',
    )
}}
with monthly_sales as (
    select
        date_trunc(date(ordered_at), month) as order_month
      , sum(subtotal) as total_sales
    from {{ ref('raw_orders') }}
    group by all
)

select * from monthly_sales