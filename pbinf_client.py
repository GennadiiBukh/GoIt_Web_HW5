import asyncio
import websockets
import json

async def main():
    uri = "ws://localhost:8080"  # Адреса сервера WebSocket
    async with websockets.connect(uri) as websocket:
        while True:
            command = input("Введіть команду: ")  # Очікуємо введення команди від користувача
            if command.lower().strip() == 'quit':
                break
            command_list = [word for word in command.lower().split(' ') if word]
            if command_list[0] != 'exchange':
                print("Неіснуюча команда")
                continue
            date_shift = command_list[1]
            add_currency_list = command_list[2:]
            if int(date_shift) > 10:
                print('Можна дізнатися курс валют не більше, ніж за останні 10 днів')
                continue
            request = {'date_shift': date_shift, 'add_currency_list': add_currency_list}
            
            await websocket.send(json.dumps(request))  # Відправляємо JSON-запит на сервер
            response = await websocket.recv()  # Очікуємо відповідь від сервера
            print(response)  # Виводимо отриману відповідь

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
