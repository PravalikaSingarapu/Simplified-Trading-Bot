"""
Limit Order Implementation for Binance Futures Trading Bot
Handles limit buy and sell orders with price validation and logging.
"""

import logging
from typing import Dict, Any, Optional
from binance.enums import *
from .basic_bot import BasicBot


class LimitOrderManager:
    """
    Manages limit order execution for Binance Futures.
    """
    
    def __init__(self, bot: BasicBot):
        """
        Initialize limit order manager.
        
        Args:
            bot (BasicBot): Instance of the basic bot
        """
        self.bot = bot
        self.logger = bot.logger
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict[str, Any]]:
        """
        Place a limit order (buy or sell).
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            side (str): Order side ('BUY' or 'SELL')
            quantity (float): Order quantity
            price (float): Limit price
            
        Returns:
            Dict containing order response or None if failed
        """
        try:
            # Validate inputs
            if not self._validate_limit_order_inputs(symbol, side, quantity, price):
                return None
            
            # Log order attempt
            self.logger.info(f"Placing limit {side} order: {quantity} {symbol} at {price}")
            
            # Place the order
            order = self.bot.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,  # Good Till Cancelled
                quantity=quantity,
                price=price
            )
            
            # Log successful order
            self.logger.info(f"Limit order placed successfully: {order}")
            
            # Get order status
            order_status = self._get_order_status(symbol, order['orderId'])
            
            return {
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'type': 'LIMIT',
                'status': order_status,
                'raw_response': order
            }
            
        except Exception as e:
            self.logger.error(f"Failed to place limit order: {str(e)}")
            return None
    
    def _validate_limit_order_inputs(self, symbol: str, side: str, quantity: float, price: float) -> bool:
        """
        Validate limit order inputs.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side
            quantity (float): Order quantity
            price (float): Limit price
            
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
        
        # Validate price
        if price <= 0:
            self.logger.error(f"Invalid price: {price}. Must be positive")
            return False
        
        # Check price precision
        if not self._validate_price_precision(symbol, price):
            return False
        
        return True
    
    def _validate_price_precision(self, symbol: str, price: float) -> bool:
        """
        Validate price precision according to symbol requirements.
        
        Args:
            symbol (str): Trading symbol
            price (float): Price to validate
            
        Returns:
            bool: True if price precision is valid
        """
        try:
            symbol_info = self.bot.get_symbol_info(symbol)
            if not symbol_info:
                return False
            
            for filter_item in symbol_info['filters']:
                if filter_item['filterType'] == 'PRICE_FILTER':
                    tick_size = float(filter_item['tickSize'])
                    
                    # Use tolerance-aware comparison to handle floating-point precision
                    rounded_price = round(price / tick_size) * tick_size
                    tolerance = tick_size * 1e-10  # Very small tolerance relative to tick size
                    
                    if abs(price - rounded_price) <= tolerance:
                        return True
                    else:
                        self.logger.error(f"Price {price} doesn't match tick size {tick_size} for {symbol}. "
                                        f"Nearest valid price: {rounded_price}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating price precision: {str(e)}")
            return False
    
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
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """
        Cancel an existing order.
        
        Args:
            symbol (str): Trading symbol
            order_id (int): Order ID to cancel
            
        Returns:
            bool: True if cancellation successful
        """
        try:
            result = self.bot.client.futures_cancel_order(
                symbol=symbol.upper(),
                orderId=order_id
            )
            
            self.logger.info(f"Order {order_id} cancelled successfully: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get open orders for a symbol or all symbols.
        
        Args:
            symbol (str, optional): Trading symbol. If None, gets all open orders.
            
        Returns:
            List of open orders
        """
        try:
            if symbol:
                orders = self.bot.client.futures_get_open_orders(symbol=symbol.upper())
            else:
                orders = self.bot.client.futures_get_open_orders()
            
            self.logger.info(f"Retrieved {len(orders)} open orders")
            return orders
            
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {str(e)}")
            return []