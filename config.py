
PG_USER = 'app'
PG_PASSWORD = '1234'
PG_HOST = '0.0.0.0'
PG_DB = 'person'
PG_DSN = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:5432/{PG_DB}'
PG_DSN_ALC = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:5432/{PG_DB}'

BASE_URL = 'https://swapi.dev/api/people'
COUNT = 82
