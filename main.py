import asyncio
from src.bybit_trading_bot import BybitTradingBot


async def main():
    # Initialize bot (loads credentials from .env automatically)
    bot = BybitTradingBot()
    
    print("Starting Bitcoin market data stream...")
    print("Press Ctrl+C to stop")
    
    try:
        await bot.subscribe_to_bitcoin_ticker()
    except KeyboardInterrupt:
        print("\nStopping market data stream...")


if __name__ == "__main__":
    asyncio.run(main())