# MSTR Simulator 2.0 Walkthrough

I have upgraded the MicroStrategy Simulator to be more accurate and feature-rich.

## Key Improvements

### 1. Convertible Debt Logic
The simulator now correctly models **Convertible Senior Notes**.
- **Old Behavior**: Debt was treated as a hard liability that *must* be repaid in cash at maturity.
- **New Behavior**: If MSTR's stock price is above the conversion price at maturity, the debt automatically converts into shares. This avoids the artificial "liquidity crisis" in bull markets and correctly models the dilution instead.

### 2. Monthly Resolution
The simulation now runs on a **monthly** basis instead of yearly.
- This captures short-term volatility and liquidity crunches that could kill the company in a bad month, even if the year "on average" looked fine.

### 3. Live Data Fetching
Added a "Fetch Live Data" button that pulls real-time market data:
- **BTC Price**: Live from Yahoo Finance.
- **MSTR Price**: Live from Yahoo Finance.
- **Shares Outstanding**: Live estimate.

### 4. Dynamic Premium
Implemented a dynamic premium model where the NAV multiplier ($\lambda$) compresses during Bitcoin drawdowns, accelerating the "death spiral" effect in bear scenarios.

## Verification
I launched the app and verified the UI loads correctly with the new Plotly charts and Sidebar configuration.

![App Screenshot](/Users/konstantinosfotiou/.gemini/antigravity/brain/7634066e-0d7a-49f2-8136-69f962458f38/mstr_simulator_2_0_1763719042047.png)

## How to Run
```bash
streamlit run app.py
```
