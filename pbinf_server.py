import sys
from datetime import datetime, timedelta
import asyncio
import platform
import aiohttp
import websockets
import json

class HttpError(Exception):
    pass

async def request(url: str):
    async with aiohttp.ClientSession() as client:
        try:
            async with client.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    raise HttpError(f"Error status: {response.status} for {url}")
        except aiohttp.ClientConnectorError:
            print(f"Помилка: тайм-аут запиту для {url}")
            return None

async def main(index_day):
    d = datetime.now() - timedelta(days=index_day)
    shift = d.strftime("%d.%m.%Y")
    try:
        response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        return response
    except HttpError as err:
        print(err)
        return None

async def send_exchange_rates(websocket, path):
    async for message in websocket:
        try:
            currency_list = ['USD', 'EUR']
            data = json.loads(message)
            date_shift = int(data.get('date_shift', 1))
            add_currency_list = data.get('add_currency_list', None)
            if add_currency_list:
                currency_list.extend([item.upper() for item in add_currency_list])
            results = []

            for num in range(0, date_shift):
                r = await main(num)
                result = format_exchange_rates(r, currency_list)
                results.append(result)

            response = {'exchange_rates': results}
            await websocket.send(json.dumps(response))
        except Exception as e:
            print(f"Помилка: {e}")
            await websocket.send(json.dumps({'error': 'Помилка обробки запиту'}))

def format_exchange_rates(data, currency_list):
    if data is not None:
        result = {'date': data['date'], 'exchangeRate': []}

        for rate in data['exchangeRate']:
            if rate['currency'] in currency_list:
                result['exchangeRate'].append({
                    'currency': rate['currency'],
                    'Sale': rate['saleRate'],
                    'Purchase': rate['purchaseRate']
                })

        return result

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    start_server = websockets.serve(send_exchange_rates, "localhost", 8080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
