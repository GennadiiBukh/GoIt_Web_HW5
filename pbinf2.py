import sys
from datetime import datetime, timedelta
import httpx
import asyncio
import platform

class HttpError(Exception):
    pass

async def request(url: str):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=5.0)  # Встановлюємо тайм-аут на 5 секунд
            if r.status_code == 200:
                result = r.json()
                return result
            else:
                raise HttpError(f"Error status: {r.status_code} for {url}")
        except httpx.ReadTimeout:
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
    print('\n', sys.argv)
    date_shift = int(sys.argv[1])
    if date_shift > 10:
        print('Можна дізнатися курс валют не більше, ніж за останні 10 днів')
    else:
        loop = asyncio.get_event_loop()
        tasks = [main(num) for num in range(0, date_shift)]
        results = loop.run_until_complete(asyncio.gather(*tasks))

        for r in results:
            if r is not None:                
                seek_date = r['date']
                print('\n',seek_date)
                for rate in r['exchangeRate']:
                    if rate['currency'] in ['USD', 'EUR']:                                                        
                        print('\n',rate['currency'])
                        print('Sale: ', rate['saleRate'])
                        print('Purchase: ', rate['purchaseRate'])                
            else:
                print("Помилка: не отримано відповіді вчасно (тайм-аут)")
