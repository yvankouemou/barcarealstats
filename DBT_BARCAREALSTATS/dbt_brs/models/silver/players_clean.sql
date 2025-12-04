{{ config(
    materialized='view'
) }}

SELECT
    -- Toutes les colonnes de player sauf firstname et lastname
    STRUCT(
        player.id AS id,
        player.name AS name,
        player.age AS age,
        player.birth AS birth,
        player.nationality AS nationality,
        player.height AS height,
        player.weight AS weight,
        player.injured AS injured,
        player.photo AS photo
    ) AS player,
    statistics
FROM {{ ref('players_bronze') }}
