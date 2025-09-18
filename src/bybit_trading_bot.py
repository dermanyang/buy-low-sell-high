import asyncio
import json
import os
import websockets
from pybit.unified_trading import HTTP
from dotenv import load_dotenv

load_dotenv()


class BybitTradingBot:
    def __init__(self, api_key=None, api_secret=None, testnet=None):
        self.api_key = api_key or os.getenv('BYBIT_API_KEY')
        self.api_secret = api_secret or os.getenv('BYBIT_API_SECRET')
        self.testnet = testnet if testnet is not None else os.getenv('BYBIT_TESTNET', 'true').lower() == 'true'
        self.ws_url = "wss://stream-testnet.bybit.com/v5/public/linear" if self.testnet else "wss://stream.bybit.com/v5/public/linear"
        
        # Store the latest ticker data to avoid None values from delta updates
        self.latest_ticker = {}
        
        if self.api_key and self.api_secret:
            self.session = HTTP(
                testnet=self.testnet,
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
        else:
            self.session = HTTP(testnet=self.testnet)
    
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
                            # Update latest ticker with new data (delta or snapshot)
                            self.latest_ticker.update(ticker_data)
                            
                            # Only print updates when we have meaningful changes
                            if any(key in ticker_data for key in ['lastPrice', 'indexPrice', 'price24hPcnt']):
                                print(f"Bitcoin Price Update:")
                                print(f"  Symbol: {self.latest_ticker.get('symbol', 'BTCUSDT')}")
                                
                                index_price = self.latest_ticker.get('indexPrice')
                                
                                try:
                                    if index_price:
                                        print(f"  Spot Index Price: ${float(index_price):,.2f}")
                                    
                                    change = self.latest_ticker.get('price24hPcnt')
                                    if change:
                                        print(f"  24h Change: {float(change):.2f}%")
                                    
                                    volume = self.latest_ticker.get('volume24h')
                                    if volume:
                                        print(f"  Volume 24h: {float(volume):,.2f} BTC")
                                    
                                    high = self.latest_ticker.get('highPrice24h')
                                    low = self.latest_ticker.get('lowPrice24h')
                                    if high:
                                        print(f"  High 24h: ${float(high):,.2f}")
                                    if low:
                                        print(f"  Low 24h: ${float(low):,.2f}")
                                except (ValueError, TypeError) as e:
                                    print(f"  Error formatting price data: {e}")
                                
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