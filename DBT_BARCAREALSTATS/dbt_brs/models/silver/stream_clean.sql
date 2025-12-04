{{ config(
    materialized='view'
) }}

WITH base AS (
    SELECT
        r.time,
        r.team,
        r.player,
        r.assist,
        r.type,
        r.detail,
        r.comments
    FROM {{ ref('stream_bronze') }},
         UNNEST(response) AS r
)

SELECT *
FROM base
