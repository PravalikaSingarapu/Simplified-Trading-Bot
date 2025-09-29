# Simplified-Trading-Bot
Overview

A CLI-based trading bot for Binance USDT-M Futures that enables automated cryptocurrency trading through command-line interface. The bot supports core trading functionality including market orders, limit orders, and provides a foundation for advanced order types like Stop-Limit, OCO (One-Cancels-the-Other), TWAP (Time-Weighted Average Price), and Grid trading strategies. Built with Python and the Binance API, it includes comprehensive logging, input validation, and testnet support for safe development and testing.
User Preferences

Preferred communication style: Simple, everyday language.
System Architecture
Core Architecture Pattern

The application follows a modular, object-oriented architecture with clear separation of concerns. The main components are organized into core trading functionality and advanced features, with a shared base class providing common infrastructure.
CLI Interface Design

Uses Python's argparse library to provide a command-line interface with subcommands for different order types. The main.py serves as the entry point, parsing arguments and delegating to appropriate order managers. This design allows for extensible command structures and consistent argument handling across different order types.
Trading Bot Infrastructure

BasicBot Class: Central component that handles Binance API authentication, connection management, logging setup, and common validation logic. All order managers depend on this shared infrastructure, ensuring consistent error handling and logging across the system.

Order Manager Pattern: Separate manager classes for different order types (MarketOrderManager, LimitOrderManager, etc.), each encapsulating specific trading logic while leveraging the shared BasicBot infrastructure. This pattern allows for easy extension with new order types.
Authentication and Security

API credentials are handled through command-line arguments or environment variables, with testnet mode enabled by default for safe development. The authentication is centralized in the BasicBot class and shared across all order managers.
Logging Architecture

Structured logging system captures all trading activities, API calls, errors, and executions. Logging is configured at the BasicBot level and inherited by all order managers, ensuring consistent log format and centralized log management.
Validation Strategy

Input validation is implemented at multiple levels - command-line argument parsing, order-specific validation in each manager, and API-level validation through the Binance client. This layered approach ensures data integrity and prevents invalid trades.
Extensibility Design

The architecture supports future expansion through the advanced orders package structure. Base functionality is implemented with placeholder methods for bonus features (Stop-Limit, OCO, TWAP, Grid trading), allowing for incremental development without breaking existing functionality.
External Dependencies
Primary Trading API

Binance API: Core integration through the python-binance library for futures trading operations, account management, and market data. Supports both live trading and testnet environments.
Python Libraries

argparse: Command-line interface parsing and help generation logging: Structured logging for trading activities and error tracking decimal: Precise numerical calculations for trading quantities and prices time: Time-based operations for order timing and strategy execution
Development Environment

Testnet Support: Binance testnet integration for safe development and testing without real money Environment Variables: Support for secure credential management through system environment variables
Future Integrations

The advanced order types are structured to potentially integrate additional services for enhanced trading strategies, including external data feeds for TWAP calculations and grid trading optimization algorithms.
