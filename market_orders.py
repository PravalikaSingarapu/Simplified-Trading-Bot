"""
Market Order Implementation for Binance Futures Trading Bot
Handles market buy and sell orders with validation and logging.
"""

import logging
from typing import Dict, Any, Optional
from binance.enums import *
from .basic_bot import BasicBot


class MarketOrderManager:
    """
    Manages market order execution for Binance Futures.
    """
    
    def __init__(self, bot: BasicBot):
        """
        Initialize market order manager.
        
        Args:
            bot (BasicBot): Instance of the basic bot
        """
        self.bot = bot
        self.logger = bot.logger
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict[str, Any]]:
        """
        Place a market order (buy or sell).
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            side (str): Order side ('BUY' or 'SELL')
            quantity (float): Order quantity
            
        Returns:
            Dict containing order response or None if failed
        """
        try:
            # Validate inputs
            if not self._validate_market_order_inputs(symbol, side, quantity):
                return None
            
            # Log order attempt
            self.logger.info(f"Placing market {side} order: {quantity} {symbol}")
            
            # Place the order
            order = self.bot.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            # Log successful order
            self.logger.info(f"Market order placed successfully: {order}")
            
            # Get order status
            order_status = self._get_order_status(symbol, order['orderId'])
            
            return {
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'type': 'MARKET',
                'status': order_status,
                'raw_response': order
            }
            
        except Exception as e:
            self.logger.error(f"Failed to place market order: {str(e)}")
            return None
    
    def _validate_market_order_inputs(self, symbol: str, side: str, quantity: float) -> bool:
        """
        Validate market order inputs.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side
            quantity (float): Order quantity
            
        Returns:
            bool: True if inputs are valid
        """
        # Validate symbol
        if not self.bot.validate_symbol(symbol):
            self.logger.error(f"Invalid symbol: {symbol}")
            return False
        
        # Validate side
        if side.upper() not in ['BUY', 'SELL']:
            self.logger.error(f"Invalid order side: {side}. Must be 'BUY' or 'SELL'")
            return False
        
        # Validate quantity
        if quantity <= 0:
            self.logger.error(f"Invalid quantity: {quantity}. Must be positive")
            return False
        
        if not self.bot.validate_quantity(symbol, quantity):
            return False
        
        return True
    
    def _get_order_status(self, symbol: str, order_id: int) -> Optional[str]:
        """
        Get the current status of an order.
        
        Args:
            symbol (str): Trading symbol
            order_id (int): Order ID
            
        Returns:
            str: Order status or None if error
        """
        try:
            order_info = self.bot.client.futures_get_order(
                symbol=symbol.upper(),
                orderId=order_id
            )
            return order_info.get('status')
            
        except Exception as e:
            self.logger.error(f"Failed to get order status: {str(e)}")
            return None
    
    def get_recent_trades(self, symbol: str, limit: int = 10) -> list:
        """
        Get recent trades for a symbol.
        
        Args:
            symbol (str): Trading symbol
            limit (int): Number of trades to retrieve
            
        Returns:
            List of recent trades or None if error
        """
        try:
            trades = self.bot.client.futures_account_trades(
                symbol=symbol.upper(),
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(trades)} recent trades for {symbol}")
            return trades
            
        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {str(e)}")
            return []