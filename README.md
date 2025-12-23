# MicroStrategy Goes Boom 💥

A **toy, deterministic model** of MicroStrategy/Strategy Inc.'s capital structure, viewed through a ~~Ponzi-lens~~ *speculative leverage model*. This interactive Streamlit app simulates how the company's leveraged Bitcoin strategy could evolve under different scenarios.

## 🎯 What This Does

The model simulates a MicroStrategy-style capital structure where:
- The system survives as long as **new capital inflows** plus existing cash and BTC sales can meet **cash obligations** (opex, coupons, debt maturities)
- You can test different scenarios: Bull, Base, Bear, or fully Custom
- The model tracks: BTC price, holdings, cash balance, NAV, market cap, obligations, and capital inflows
- It flags **collapse scenarios** when equity is wiped out or funding gaps can't be filled

⚠️ **Disclaimer**: This is NOT investment advice, NOT a precise forecast, and ignores lots of real-world nuance. Use it as an intuition-building sandbox.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/microstrategy-goes-boom.git
cd microstrategy-goes-boom
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501` (should open automatically)

## 📊 Features

### Scenario Presets
- **Bull (BTC moon)**: 20% annual BTC growth
- **Base (modest BTC)**: 8% annual BTC growth
- **Bear (BTC stagnation)**: 0% annual BTC growth
- **Custom**: Set your own parameters

### Adjustable Parameters
- Initial BTC price and holdings
- BTC annual growth rate
- Senior debt and preferred stock amounts
- Interest rates and coupon rates
- Operating cash burn
- Maximum annual capital raise capacity
- Equity premium multiple over NAV
- Debt maturity schedule

### Visualizations
1. **BTC Price & Holdings**: Track price appreciation and holdings over time
2. **Balance Sheet**: Asset value vs senior claims vs NAV equity
3. **Cash Flow**: Cash obligations vs capital inflows
4. **Stress Indicators**: Funding gaps and BTC sales

## 🏗️ Model Architecture

The simulation uses a simplified yearly model that tracks:

**State Variables:**
- BTC price (grows deterministically)
- BTC holdings (depleted if funding gaps occur)
- Cash balance
- Asset value = (BTC price × holdings) + cash
- Senior claims = debt + preferred stock
- NAV equity = max(assets - senior claims, 0)
- Market cap = NAV × equity premium λ

**Cash Flow Logic:**
- **Obligations** = debt interest + preferred dividends + operating expenses + debt maturities
- **Inflows** = new capital raises (capped at % of market cap)
- **Funding Gap** = obligations - (cash + inflows)
- If gap > 0, sell BTC to cover
- If not enough BTC → **COLLAPSE** 💥

## 🎮 How to Use

1. **Pick a scenario** from the sidebar or go Custom
2. **Adjust parameters** to test different assumptions
3. **Watch the charts** to see when/if collapse occurs
4. **Iterate** to understand which factors matter most

### Interesting Questions to Explore

- What BTC growth rate is needed for long-term survival?
- How sensitive is the model to equity premium assumptions?
- What happens when debt maturities hit in 2028/2030?
- Can the company survive a 50% BTC drawdown?
- How much does operating cash burn matter vs. capital structure?

## 📁 Project Structure

```
microstrategy-goes-boom/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── generate_preview.py # Social media preview image generator
├── preview.png        # Preview image for social sharing (1200x630)
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## 🌐 Social Media Preview

The app includes optimized Open Graph meta tags for better link previews on WhatsApp, Twitter, Facebook, and other platforms.

### Regenerating the Preview Image

If you want to customize the social media preview image:

```bash
python generate_preview.py
```

This creates a 1200x630px preview image optimized for all social platforms.

## 🛠️ Tech Stack

- **Streamlit**: Web app framework
- **NumPy**: Numerical computing
- **Pandas**: Data manipulation
- **Matplotlib**: Plotting and visualization

## 🤝 Contributing

This is a toy model for educational purposes. Feel free to:
- Fork and experiment
- Submit PRs with improvements
- Open issues for bugs or suggestions
- Add new scenarios or features

## 📜 License

MIT License - feel free to use, modify, and distribute as you wish.

## 🙏 Acknowledgments

Inspired by the fascinating capital structure engineering of MicroStrategy/Strategy Inc. and the broader discourse around leveraged Bitcoin strategies.

---

**Remember**: This is a simplified model. Real financial systems are vastly more complex. Always do your own research and consult with financial professionals before making investment decisions.

