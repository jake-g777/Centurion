# CS2 Skin Arbitrage Tool

A comprehensive tool for finding arbitrage opportunities across CS2 skin marketplaces including CSFloat, Steam Marketplace, and other popular platforms.

## Features

- **Multi-Marketplace Integration**: Monitor prices from CSFloat, Steam Marketplace, and other CS2 skin marketplaces
- **Real-time Price Tracking**: Continuously monitor price changes
- **Arbitrage Detection**: Automatically identify profitable arbitrage opportunities
- **Web Dashboard**: Beautiful web interface for monitoring opportunities
- **Historical Data**: Track price history and trends
- **Alert System**: Get notified when profitable opportunities arise

## Supported Marketplaces

- CSFloat
- Steam Marketplace
- Buff.163
- Skinport
- DMarket
- Bitskins

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Centurion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. Run the application:
```bash
python main.py
```

## Usage

1. **Start the web dashboard**: Navigate to `http://localhost:8000`
2. **Search for skins**: Enter weapon names or skin names
3. **Monitor opportunities**: View real-time arbitrage opportunities
4. **Set alerts**: Configure price alerts for specific skins

## Configuration

Edit the `.env` file to configure:
- API keys for various marketplaces
- Database settings
- Alert thresholds
- Update intervals

## API Endpoints

- `GET /api/skins/{skin_name}` - Get current prices for a skin
- `GET /api/opportunities` - Get current arbitrage opportunities
- `POST /api/alerts` - Set up price alerts
- `GET /api/history/{skin_name}` - Get price history for a skin

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details 