# Elite Dangerous Discord Bot

## Overview

This is a Discord bot designed for Elite Dangerous players to facilitate colonization commodity delivery contracts. The bot provides quote requests, contract management, and pricing calculations for transporting commodities between star systems within the Elite Dangerous universe.

## System Architecture

### Frontend Architecture
- **Discord Bot Interface**: Built using discord.py with slash commands for user interaction
- **Command System**: Modular command structure with app_commands for modern Discord slash command support
- **User Interface**: Simple command-based interaction through Discord's native interface

### Backend Architecture
- **Python-based Bot**: Core bot functionality built with discord.py framework
- **Modular Design**: Separated concerns across multiple modules:
  - `main.py`: Bot initialization and startup
  - `bot/commands.py`: Command handling and user interaction
  - `bot/contract_manager.py`: Contract lifecycle management
  - `bot/pricing.py`: Dynamic pricing calculations
  - `bot/validation.py`: Input validation for systems and commodities

### Data Storage Solutions
- **JSON File Storage**: Currently uses local JSON files for commodity and system data
- **In-Memory Storage**: Contract data stored in memory (temporary solution)
- **Future Database Ready**: Architecture designed to easily integrate with Postgres database

## Key Components

### Contract Management System
- **Contract Creation**: Generates unique contract IDs for commodity delivery requests
- **Contract Lifecycle**: Tracks contracts from creation through completion
- **Expiration System**: Automatic cleanup of expired contracts (24-hour expiry)
- **Status Tracking**: Pending, accepted, and completed contract states

### Pricing Engine
- **Dynamic Pricing**: Calculates quotes based on multiple factors:
  - Base commodity prices
  - System distances
  - Risk premiums (15%)
  - Fuel costs per light-year
  - Time value multipliers for long routes
- **Commodity Database**: Comprehensive pricing data for Elite Dangerous commodities
- **Distance Calculations**: Real Elite Dangerous system coordinates for accurate pricing

### Validation System
- **System Validation**: Validates star system names against Elite Dangerous universe
- **Commodity Validation**: Ensures requested commodities exist and are available
- **Input Sanitization**: Robust validation for user inputs

### Command System
- **Slash Commands**: Modern Discord slash command implementation
- **Quote Requests**: `/request_quote` command for commodity delivery quotes
- **Parameter Validation**: Comprehensive input validation and error handling

## Data Flow

1. **User Request**: User submits quote request via `/request_quote` slash command
2. **Input Validation**: System validates commodities, quantities, and system names
3. **Price Calculation**: Pricing engine calculates delivery costs based on multiple factors
4. **Contract Creation**: Contract manager creates new contract with unique ID
5. **Response Generation**: Bot returns formatted quote with contract details
6. **Contract Management**: System tracks contract lifecycle and handles expiration

## External Dependencies

### Discord Integration
- **discord.py**: Primary Discord API wrapper
- **Bot Permissions**: Requires basic bot permissions (no privileged intents currently)
- **Slash Commands**: Uses Discord's application command system

### Elite Dangerous Data
- **System Coordinates**: Real Elite Dangerous galaxy coordinates
- **Commodity Prices**: Based on actual in-game commodity values
- **Distance Calculations**: Accurate interstellar distance calculations

## Deployment Strategy

### Environment Configuration
- **Environment Variables**: Discord bot token stored in `DISCORD_TOKEN` environment variable
- **Logging**: Comprehensive logging system for debugging and monitoring
- **Error Handling**: Robust error handling for network and API failures

### Scalability Considerations
- **Stateless Design**: Bot designed to be stateless for easy scaling
- **Database Ready**: Architecture prepared for database integration
- **Memory Management**: Automatic cleanup of expired contracts

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 04, 2025. Initial setup

## Technical Notes

### Current Limitations
- **In-Memory Storage**: Contract data not persisted between bot restarts
- **Single Instance**: Currently designed for single bot instance
- **Local Data Files**: System and commodity data stored in local JSON files

### Future Enhancements
- **Database Integration**: Ready for Postgres database integration
- **Persistent Storage**: Contract data persistence across restarts
- **Multi-Guild Support**: Enhanced support for multiple Discord servers
- **Advanced Pricing**: More sophisticated pricing algorithms
- **Contract Fulfillment**: Complete contract lifecycle management

### Security Considerations
- **Input Validation**: Comprehensive validation prevents injection attacks
- **Rate Limiting**: Discord API rate limiting handled by discord.py
- **Error Handling**: Graceful error handling prevents information leakage