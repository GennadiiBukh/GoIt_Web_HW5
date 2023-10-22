import sys
from datetime import datetime, timedelta

import asyncio
import platform
import aiohttp

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

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())      

    currency_list = ['USD', 'EUR']

    print('\n', sys.argv)
    date_shift = int(sys.argv[1])

    if len(sys.argv) > 2:                # Якщо в командному рядку додані інші валюти - додаємо їх до списку виводу        
        add_currency = [item.upper() for item in sys.argv[2:]]
        currency_list.extend(add_currency)
    
    if date_shift > 10:
        print('Можна дізнатися курс валют не більше, ніж за останні 10 днів')
    else:
        loop = asyncio.get_event_loop()
        tasks = [main(num) for num in range(0, date_shift)]
        results = loop.run_until_complete(asyncio.gather(*tasks))

        for r in results:
            if r is not None:                
                seek_date = r['date']
                print('_____________________________________________________________________________________')
                print('\n',seek_date)
                for rate in r['exchangeRate']:
                    if rate['currency'] in currency_list:                                                        
                        print('\n',rate['currency'])
                        print('Sale: ', rate['saleRate'])
                        print('Purchase: ', rate['purchaseRate'])                
            else:
                print("Помилка: не отримано відповіді вчасно (тайм-аут)")
