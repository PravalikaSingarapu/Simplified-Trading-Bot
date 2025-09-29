#!/usr/bin/env python3
"""
Binance Futures Trading Bot - Main Entry Point
CLI-based trading bot for Binance USDT-M Futures with market and limit orders.
"""

import argparse
import sys
import os
from src.basic_bot import BasicBot
from src.market_orders import MarketOrderManager
from src.limit_orders import LimitOrderManager


def setup_cli():
    """Setup command line interface."""
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place market buy order
  python main.py market BTCUSDT buy 0.001 --api-key YOUR_KEY --api-secret YOUR_SECRET
  
  # Place limit sell order
  python main.py limit ETHUSDT sell 0.01 --price 2500.0 --api-key YOUR_KEY --api-secret YOUR_SECRET
  
  # Get account balance
  python main.py balance --api-key YOUR_KEY --api-secret YOUR_SECRET
        """
    )
    
    # Global arguments
    parser.add_argument('--api-key', required=False, 
                       help='Binance API key (or set BINANCE_API_KEY env var)')
    parser.add_argument('--api-secret', required=False,
                       help='Binance API secret (or set BINANCE_API_SECRET env var)')
    parser.add_argument('--testnet', action='store_true', default=True,
                       help='Use testnet (default: True)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Market order command
    market_parser = subparsers.add_parser('market', help='Place market orders')
    market_parser.add_argument('symbol', help='Trading pair (e.g., BTCUSDT)')
    market_parser.add_argument('side', choices=['buy', 'sell'], help='Order side')
    market_parser.add_argument('quantity', type=float, help='Order quantity')
    
    # Limit order command
    limit_parser = subparsers.add_parser('limit', help='Place limit orders')
    limit_parser.add_argument('symbol', help='Trading pair (e.g., BTCUSDT)')
    limit_parser.add_argument('side', choices=['buy', 'sell'], help='Order side')
    limit_parser.add_argument('quantity', type=float, help='Order quantity')
    limit_parser.add_argument('--price', type=float, required=True, help='Limit price')
    
    # Balance command
    balance_parser = subparsers.add_parser('balance', help='Get account balance')
    
    # Orders command
    orders_parser = subparsers.add_parser('orders', help='Get open orders')
    orders_parser.add_argument('--symbol', help='Symbol to filter orders (optional)')
    
    # Demo command (no API keys required)
    demo_parser = subparsers.add_parser('demo', help='Demo mode - show interface without API calls')
    
    return parser


def get_credentials(args):
    """Get API credentials from arguments or environment variables."""
    api_key = args.api_key or os.getenv('BINANCE_API_KEY')
    api_secret = args.api_secret or os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: API credentials required!")
        print("Provide --api-key and --api-secret arguments")
        print("Or set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")
        sys.exit(1)
    
    return api_key, api_secret


def handle_demo():
    """Handle demo command - show interface without API calls."""
    print("🤖 Binance Futures Trading Bot - Demo Mode")
    print("=" * 50)
    print()
    print("This bot supports the following features:")
    print()
    print("📈 Market Orders:")
    print("  - Place immediate buy/sell orders at current market price")
    print("  - Example: python main.py market BTCUSDT buy 0.001")
    print()
    print("📊 Limit Orders:")
    print("  - Place orders at specific price levels")
    print("  - Example: python main.py limit ETHUSDT sell 0.01 --price 2500.0")
    print()
    print("💰 Account Balance:")
    print("  - Check your USDT-M Futures account balance")
    print("  - Example: python main.py balance")
    print()
    print("📋 Open Orders:")
    print("  - View current open orders")
    print("  - Example: python main.py orders")
    print()
    print("🔧 Configuration:")
    print("  - Uses Binance Testnet by default for safe testing")
    print("  - Comprehensive logging to bot.log file")
    print("  - Input validation for symbols, quantities, and prices")
    print()
    print("To use with real API credentials:")
    print("1. Get testnet credentials from https://testnet.binancefuture.com")
    print("2. Run: python main.py [command] --api-key YOUR_KEY --api-secret YOUR_SECRET")
    print()
    print("Demo completed! ✨")


def handle_market_order(bot, market_manager, args):
    """Handle market order command."""
    print(f"Placing market {args.side} order for {args.quantity} {args.symbol}")
    
    result = market_manager.place_market_order(args.symbol, args.side, args.quantity)
    
    if result:
        print(f"✅ Market order placed successfully!")
        print(f"Order ID: {result['order_id']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Side: {result['side']}")
        print(f"Quantity: {result['quantity']}")
        print(f"Status: {result['status']}")
    else:
        print("❌ Failed to place market order. Check logs for details.")


def handle_limit_order(bot, limit_manager, args):
    """Handle limit order command."""
    print(f"Placing limit {args.side} order for {args.quantity} {args.symbol} at {args.price}")
    
    result = limit_manager.place_limit_order(args.symbol, args.side, args.quantity, args.price)
    
    if result:
        print(f"✅ Limit order placed successfully!")
        print(f"Order ID: {result['order_id']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Side: {result['side']}")
        print(f"Quantity: {result['quantity']}")
        print(f"Price: {result['price']}")
        print(f"Status: {result['status']}")
    else:
        print("❌ Failed to place limit order. Check logs for details.")


def handle_balance(bot):
    """Handle balance command."""
    print("Getting account balance...")
    
    balance = bot.get_account_balance()
    
    if balance:
        print("💰 Account Balance:")
        print(f"Total Wallet Balance: {balance['total_wallet_balance']:.4f} USDT")
        print(f"Available Balance: {balance['available_balance']:.4f} USDT")
        print(f"Total Unrealized PnL: {balance['total_unrealized_pnl']:.4f} USDT")
        print(f"Total Margin Balance: {balance['total_margin_balance']:.4f} USDT")
    else:
        print("❌ Failed to get account balance. Check logs for details.")


def handle_orders(limit_manager, args):
    """Handle orders command."""
    print(f"Getting open orders{' for ' + args.symbol if args.symbol else ''}...")
    
    orders = limit_manager.get_open_orders(args.symbol)
    
    if orders:
        print(f"📋 Found {len(orders)} open orders:")
        for order in orders:
            print(f"Order ID: {order['orderId']}, Symbol: {order['symbol']}, "
                  f"Side: {order['side']}, Quantity: {order['origQty']}, "
                  f"Price: {order['price']}, Status: {order['status']}")
    else:
        print("No open orders found.")


def main():
    """Main entry point."""
    parser = setup_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Handle demo command first (no credentials needed)
        if args.command == 'demo':
            handle_demo()
            return
        
        # Get credentials for other commands
        api_key, api_secret = get_credentials(args)
        
        # Initialize bot
        print("🤖 Initializing Binance Futures Trading Bot...")
        bot = BasicBot(api_key, api_secret, testnet=args.testnet)
        
        # Initialize managers
        market_manager = MarketOrderManager(bot)
        limit_manager = LimitOrderManager(bot)
        
        # Handle commands
        if args.command == 'market':
            handle_market_order(bot, market_manager, args)
        elif args.command == 'limit':
            handle_limit_order(bot, limit_manager, args)
        elif args.command == 'balance':
            handle_balance(bot)
        elif args.command == 'orders':
            handle_orders(limit_manager, args)
        
    except KeyboardInterrupt:
        print("\n⏹️  Trading bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()