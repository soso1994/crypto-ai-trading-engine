# Binance WebSocket consumer (skeleton)
# server/src/feeds/binance_ws.py
import asyncio
import json
import logging
import websockets

LOGGER = logging.getLogger("datafeeds.binance")

# This is a lightweight public websocket consumer for Binance.
# - reconnect/backoff
# - sequence/backfill hooks (placeholders)
# - writes to provided writer callback (DB or local file)

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"

async def handle_message(msg, writer):
    # msg: dict
    # convert and validate as needed
    await writer(msg)

async def consumer(symbols, writer, run_forever=True):
    # symbols: list of lowercase symbol strings, e.g. ["btcusdt@depth@100ms", "btcusdt@kline_1m"]
    stream = "/".join(symbols)
    url = f"{BINANCE_WS_URL}/{stream}"
    backoff = 1
    while True:
        try:
            async with websockets.connect(url) as ws:
                LOGGER.info("Connected to Binance WS: %s", url)
                backoff = 1
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                        await handle_message(msg, writer)
                    except Exception:
                        LOGGER.exception("Failed to process message")
        except Exception:
            LOGGER.exception("Websocket error, reconnecting in %ss", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
        if not run_forever:
            break

if __name__ == "__main__":
    async def writer(msg):
        print(json.dumps(msg)[:200])
    asyncio.run(consumer(["btcusdt@kline_1m"], writer, run_forever=False))
