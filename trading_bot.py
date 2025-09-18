import asyncio
import json
import websockets
from pybit.unified_trading import HTTP


class BybitTradingBot:
    def __init__(self, api_key=None, api_secret=None, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.ws_url = "wss://stream-testnet.bybit.com/v5/public/linear" if testnet else "wss://stream.bybit.com/v5/public/linear"
        
        if api_key and api_secret:
            self.session = HTTP(
                testnet=testnet,
                api_key=api_key,
                api_secret=api_secret,
            )
        else:
            self.session = HTTP(testnet=testnet)
    
    async def subscribe_to_bitcoin_ticker(self):
        """Subscribe to Bitcoin ticker data via websocket"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Subscribe to Bitcoin ticker
                subscribe_msg = {
                    "op": "subscribe",
                    "args": ["tickers.BTCUSDT"]
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                print("Subscribed to BTCUSDT ticker data...")
                
                # Listen for messages
                async for message in websocket:
                    data = json.loads(message)
                    
                    if data.get("topic") == "tickers.BTCUSDT":
                        ticker_data = data.get("data", {})
                        if ticker_data:
                            print(f"Bitcoin Price Update:")
                            print(f"  Symbol: {ticker_data.get('symbol')}")
                            print(f"  Last Price: ${ticker_data.get('lastPrice')}")
                            print(f"  24h Change: {ticker_data.get('price24hPcnt')}%")
                            print(f"  Volume 24h: {ticker_data.get('volume24h')}")
                            print(f"  High 24h: ${ticker_data.get('highPrice24h')}")
                            print(f"  Low 24h: ${ticker_data.get('lowPrice24h')}")
                            print("-" * 50)
                    elif data.get("success"):
                        print("Successfully subscribed to ticker data")
                        
        except Exception as e:
            print(f"WebSocket error: {e}")
    
    def place_order(self, symbol="BTCUSDT", side="Buy", order_type="Market", qty="0.001"):
        """Place an order on Bybit"""
        if not self.api_key or not self.api_secret:
            print("API credentials required for placing orders!")
            return None
            
        try:
            result = self.session.place_order(
                category="linear",
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=qty,
            )
            print(f"Order placed successfully:")
            print(f"  Order ID: {result['result']['orderId']}")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Quantity: {qty}")
            return result
            
        except Exception as e:
            print(f"Error placing order: {e}")
            return None


async def main():
    # Initialize bot (without API keys for now, just for market data)
    bot = BybitTradingBot()
    
    print("Starting Bitcoin market data stream...")
    print("Press Ctrl+C to stop")
    
    try:
        await bot.subscribe_to_bitcoin_ticker()
    except KeyboardInterrupt:
        print("\nStopping market data stream...")


if __name__ == "__main__":
    asyncio.run(main())