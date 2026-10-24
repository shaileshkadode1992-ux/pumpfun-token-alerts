
import asyncio
import json
import os
import urllib.request
import websockets

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }).encode()

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=10).read()

async def main():
    uri = "wss://pumpportal.fun/api/data"

    while True:
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({"method": "subscribeNewToken"}))
                print("Listening for new Pump.fun tokens...")

                async for raw in ws:
                    token = json.loads(raw)
                    mint = token.get("mint")
                    if not mint:
                        continue

                    name = token.get("name", "Unknown")
                    symbol = token.get("symbol", "Unknown")
                    message = (
                        f"🆕 NEW PUMP.FUN TOKEN\n\n"
                        f"Name: {name}\n"
                        f"Symbol: {symbol}\n"
                        f"Address: {mint}\n\n"
                        f"https://pump.fun/coin/{mint}"
                    )

                    try:
                        await asyncio.to_thread(send_telegram, message)
                    except Exception as exc:
                        print("Telegram error:", exc)

        except Exception as exc:
            print("Connection error:", exc)
            await asyncio.sleep(5)

asyncio.run(main())
