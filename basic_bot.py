"""
Basic Bot Class for Binance Futures Trading
Handles authentication, connection, and core functionality.
"""

import logging
import time
from decimal import Decimal
from binance import Client
from binance.enums import *
from typing import Dict, Any, Optional


class BasicBot:
    """
    Core trading bot class for Binance USDT-M Futures
    Supports market and limit orders with proper validation and logging.
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot with Binance API credentials.
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): Whether to use testnet (default: True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize Binance client
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.API_URL = 'https://testnet.binancefuture.com'
            
            self.logger.info(f"Bot initialized with testnet={'ON' if testnet else 'OFF'}")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {str(e)}")
            raise
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for the bot."""
        logger = logging.getLogger('binance_bot')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler('bot.log')
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _test_connection(self) -> bool:
        """Test connection to Binance API."""
        try:
            account_info = self.client.futures_account()
            self.logger.info("Connection to Binance API successful")
            self.logger.info(f"Account balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a trading symbol exists and is active.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            bool: True if symbol is valid
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] 
                      if s['status'] == 'TRADING']
            
            is_valid = symbol.upper() in symbols
            
            if is_valid:
                self.logger.info(f"Symbol {symbol} is valid")
            else:
                self.logger.warning(f"Symbol {symbol} is not valid or not trading")
                
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error validating symbol {symbol}: {str(e)}")
            return False
    
    def validate_quantity(self, symbol: str, quantity: float) -> bool:
        """
        Validate if the quantity meets minimum requirements.
        
        Args:
            symbol (str): Trading pair symbol
            quantity (float): Order quantity
            
        Returns:
            bool: True if quantity is valid
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol.upper():
                    for filter_item in s['filters']:
                        if filter_item['filterType'] == 'LOT_SIZE':
                            min_qty = float(filter_item['minQty'])
                            if quantity >= min_qty:
                                self.logger.info(f"Quantity {quantity} is valid for {symbol}")
                                return True
                            else:
                                self.logger.warning(f"Quantity {quantity} below minimum {min_qty} for {symbol}")
                                return False
            
            self.logger.warning(f"Could not find quantity validation info for {symbol}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error validating quantity for {symbol}: {str(e)}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a trading symbol.
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            Dict containing symbol information or None if not found
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol.upper():
                    return s
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {str(e)}")
            return None
    
    def get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        Get current account balance information.
        
        Returns:
            Dict containing balance information or None if error
        """
        try:
            account_info = self.client.futures_account()
            
            balance_info = {
                'total_wallet_balance': float(account_info.get('totalWalletBalance', 0)),
                'total_unrealized_pnl': float(account_info.get('totalUnrealizedPnL', 0)),
                'total_margin_balance': float(account_info.get('totalMarginBalance', 0)),
                'available_balance': float(account_info.get('availableBalance', 0))
            }
            
            self.logger.info(f"Account balance retrieved: {balance_info}")
            return balance_info
            
        except Exception as e:
            self.logger.error(f"Error getting account balance: {str(e)}")
            return None