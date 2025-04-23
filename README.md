# Binance DCA Bot

A simple Python script for automated Dollar-Cost Averaging (DCA) on Binance Spot market.

## Features

- Automated weekly cryptocurrency purchases
- Smart interval option to spread purchases across the week
- Test mode for safe experimentation
- State tracking to prevent over-purchasing
- Configurable investment amount and trading pair

## Requirements

- Python 3.x
- python-binance ≥ 1.0.28
- pytz

## Setup

1. Install dependencies:
```bash
pip install python-binance pytz
```

2. Configure your Binance API keys:
```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
```

3. Edit the USER SETTINGS section in `binance_dca.py`:
- Set your trading pair (e.g., BTCEUR)
- Configure investment amount and period
- Adjust timezone and other preferences

4. Add to crontab (example for daily runs):
```bash
7 9 * * * /usr/bin/python3 /path/to/binance_dca.py >>/path/to/dca.log 2>&1
```

## Safety First

- Always start with `TEST_MODE=True`
- Review the code and understand the risks
- Start with small amounts
- Monitor the bot's behavior

## License

MIT License - see [LICENSE](LICENSE) for details. 