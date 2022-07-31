import asyncio
import aiohttp
import time
from pprint import pprint
import asyncpg
import more_itertools

import config


async def get_more(session, key, url_list):
    value = []
    for url_detail in url_list:
        async with session.get(url_detail) as response:
            json_detail = await response.json()
            value.append(json_detail[key])
    return ",".join(value)


async def get_homeworld(session, url_detail):
    async with session.get(url_detail) as response:
        json_detail = await response.json()
        return json_detail['name']


async def get_character(session, character_id):
    async with session.get(f'{config.BASE_URL}/{character_id}') as response:
        json_data = await response.json()
        # pprint(json_data)
        if json_data.get('detail', None) == 'Not found':    # id 17 empty
            return None
        json_data['id'] = character_id
        json_data['films'] = await get_more(session, 'title', json_data['films'])
        json_data['homeworld'] = await get_homeworld(session, json_data['homeworld'])
        json_data['species'] = await get_more(session, 'name', json_data['species'])
        json_data['starships'] = await get_more(session, 'name', json_data['starships'])
        json_data['vehicles'] = await get_more(session, 'name', json_data['vehicles'])
        # print(f'chapter id {character_id}')
        return json_data


async def main():
    async with aiohttp.ClientSession() as session:
        chapter_coros = (get_character(session, i) for i in range(1, config.COUNT + 1))
        for characters_coros_chunk in more_itertools.chunked(chapter_coros, 10):
            result = await asyncio.gather(*characters_coros_chunk)
            await insert_characters(result)


async def prepare_data(data):
    data_for_insert = []
    for data_dict in data:
        data_temp = []
        if data_dict is None:
            continue
        for key in ['created', 'edited', 'url']:
            data_dict.pop(key, None)
        for v in data_dict.values():
            if v is None:
                v = 'n/a'
            data_temp.append(v)
        data_for_insert.append(tuple(data_temp))
    return data_for_insert


async def insert_characters(character_list):
    pool = await asyncpg.create_pool(config.PG_DSN)
    tasks = []
    prepared_data = asyncio.create_task(prepare_data(character_list))
    tasks.append(prepared_data)
    result = await asyncio.gather(*tasks)
    for data in result:
        query = "INSERT INTO characters (name, height, mass, hair_color, skin_color, eye_color, " \
                "birth_year, gender, homeworld, films, species, vehicles, starships, id) " \
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)"
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(query, data)
    await pool.close()


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
