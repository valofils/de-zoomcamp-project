-- dim_countries.sql
-- Country dimension — static reference table.

select 'ET' as country_code, 'Ethiopia'      as country_name, 'East Africa'    as sub_region union all
select 'MG',                 'Madagascar',                     'East Africa'                  union all
select 'KE',                 'Kenya',                          'East Africa'                  union all
select 'SO',                 'Somalia',                        'East Africa'                  union all
select 'SD',                 'Sudan',                          'East Africa'                  union all
select 'SS',                 'South Sudan',                    'East Africa'                  union all
select 'ML',                 'Mali',                           'West Africa'                  union all
select 'BF',                 'Burkina Faso',                   'West Africa'                  union all
select 'NE',                 'Niger',                          'West Africa'                  union all
select 'TD',                 'Chad',                           'Central Africa'               union all
select 'MZ',                 'Mozambique',                     'Southern Africa'              union all
select 'MW',                 'Malawi',                         'Southern Africa'
