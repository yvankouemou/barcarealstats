{{ config(
    materialized='view'
) }}

SELECT *
FROM {{ source('football_data_test', 'api_players_stats') }}
