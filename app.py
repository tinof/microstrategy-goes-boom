import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from dataclasses import dataclass
from typing import List, Optional

# -----------------------------
# Data Structures
# -----------------------------
@dataclass
class ConvertibleDebt:
    name: str
    principal: float
    maturity_month: int  # Month index from start (e.g., 36 = 3 years out)
    coupon_rate: float
    conversion_price: float

@dataclass
class PreferredStock:
    name: str
    principal: float
    dividend_rate: float

# -----------------------------
# Helper Functions
# -----------------------------
def fetch_live_data():
    """Fetches live BTC and MSTR data using yfinance."""
    try:
        btc = yf.Ticker("BTC-USD")
        mstr = yf.Ticker("MSTR")
        
        btc_price = btc.history(period="1d")['Close'].iloc[-1]
        mstr_price = mstr.history(period="1d")['Close'].iloc[-1]
        
        # Shares outstanding is tricky to get accurately from free APIs sometimes,
        # but let's try info. If not, fallback.
        shares_outstanding = mstr.info.get('sharesOutstanding', 275_000_000) # Fallback to ~275M
        
        return btc_price, mstr_price, shares_outstanding
    except Exception as e:
        st.warning(f"Could not fetch live data: {e}. Using defaults.")
        return None, None, None

# -----------------------------
# Core Simulation Logic
# -----------------------------
def simulate_mstr_monthly(
    n_months: int,
    btc_price_start: float,
    btc_growth_annual: float,
    btc_volatility_annual: float,
    btc_holdings_start: float,
    cash_start: float,
    shares_start: float,
    convertible_debts: List[ConvertibleDebt],
    preferred_stocks: List[PreferredStock],
    operating_burn_annual: float,
    issuance_capacity_pct_annual: float,
    base_premium: float,
    dynamic_premium: bool,
):
    """
    Monthly simulation of MSTR capital structure.
    """
    
    # Time array
    months = np.arange(n_months)
    years = months / 12.0
    
    # Pre-allocate arrays
    btc_price = np.zeros(n_months)
    mstr_stock_price = np.zeros(n_months)
    premium_mult = np.zeros(n_months)
    
    btc_holdings = np.zeros(n_months)
    cash_balance = np.zeros(n_months)
    shares_outstanding = np.zeros(n_months)
    
    debt_principal = np.zeros(n_months)
    pref_principal = np.zeros(n_months)
    
    nav_per_share = np.zeros(n_months)
    market_cap = np.zeros(n_months)
    
    inflows = np.zeros(n_months)
    outflows = np.zeros(n_months)
    btc_sold = np.zeros(n_months)
    
    # Initial State
    btc_price[0] = btc_price_start
    btc_holdings[0] = btc_holdings_start
    cash_balance[0] = cash_start
    shares_outstanding[0] = shares_start
    
    # Calculate initial debt/pref totals
    current_debts = [d for d in convertible_debts] # Copy list to modify if needed
    current_prefs = [p for p in preferred_stocks]
    
    debt_principal[0] = sum(d.principal for d in current_debts)
    pref_principal[0] = sum(p.principal for p in current_prefs)
    
    # Initial Premium
    premium_mult[0] = base_premium
    
    collapse_month = None
    collapse_reason = None

    # Monthly growth/volatility
    # Simple deterministic growth path for now to show trend, 
    # or we could add random walk. Let's stick to deterministic trend for clarity
    # but allow "scenarios" to define the path shape.
    monthly_growth = (1 + btc_growth_annual) ** (1/12) - 1
    
    for i in range(n_months):
        if i > 0:
            # 1. Update BTC Price
            btc_price[i] = btc_price[i-1] * (1 + monthly_growth)
            
            # Carry forward state
            btc_holdings[i] = btc_holdings[i-1]
            cash_balance[i] = cash_balance[i-1]
            shares_outstanding[i] = shares_outstanding[i-1]
            
            # Dynamic Premium Logic
            # If BTC drops significantly from peak or is in drawdown, premium compresses.
            # Simplified: If BTC growth is negative, premium drops.
            if dynamic_premium:
                if monthly_growth < 0:
                    premium_mult[i] = max(1.0, premium_mult[i-1] * 0.95) # Decay
                else:
                    premium_mult[i] = min(base_premium, premium_mult[i-1] * 1.02) # Recover
            else:
                premium_mult[i] = base_premium

        # 2. Calculate NAV and Stock Price
        # Assets = BTC + Cash
        assets = btc_price[i] * btc_holdings[i] + cash_balance[i]
        
        # Liabilities = Debt + Preferreds
        total_debt = sum(d.principal for d in current_debts)
        total_pref = sum(p.principal for p in current_prefs)
        
        debt_principal[i] = total_debt
        pref_principal[i] = total_pref
        
        equity_value = max(0, assets - total_debt - total_pref)
        
        if shares_outstanding[i] > 0:
            nav_per_share[i] = equity_value / shares_outstanding[i]
        else:
            nav_per_share[i] = 0
            
        # Stock Price = NAV/share * Premium
        # If NAV is 0, stock price is theoretically 0 (or option value, but let's say 0 for collapse)
        if nav_per_share[i] <= 0:
            mstr_stock_price[i] = 0
            if collapse_month is None:
                collapse_month = i
                collapse_reason = "NAV <= 0 (Insolvency)"
        else:
            mstr_stock_price[i] = nav_per_share[i] * premium_mult[i]
            
        market_cap[i] = mstr_stock_price[i] * shares_outstanding[i]

        if collapse_month is not None:
            continue # Stop simulating logic, just fill arrays

        # 3. Calculate Obligations (Monthly)
        monthly_ops_burn = operating_burn_annual / 12.0
        
        # Coupon payments
        monthly_interest = sum(d.principal * d.coupon_rate for d in current_debts) / 12.0
        monthly_dividends = sum(p.principal * p.dividend_rate for p in current_prefs) / 12.0
        
        # Maturities
        maturity_payment = 0.0
        debts_to_remove = []
        
        for debt in current_debts:
            if debt.maturity_month == i:
                # Check for Conversion!
                # If Stock Price > Conversion Price, debt converts to shares.
                if mstr_stock_price[i] > debt.conversion_price:
                    # Convert!
                    new_shares = debt.principal / debt.conversion_price
                    shares_outstanding[i] += new_shares
                    # Principal is extinguished without cash
                    debts_to_remove.append(debt)
                else:
                    # Must repay in cash
                    maturity_payment += debt.principal
                    debts_to_remove.append(debt)
        
        # Remove matured/converted debts
        for d in debts_to_remove:
            current_debts.remove(d)
            
        total_obligations = monthly_ops_burn + monthly_interest + monthly_dividends + maturity_payment
        outflows[i] = total_obligations
        
        # 4. Funding & Inflows
        # Issuance Capacity (Monthly limit)
        # Max we can raise is % of Market Cap / 12
        max_issuance = (issuance_capacity_pct_annual / 12.0) * market_cap[i]
        
        # We only raise what we need? Or do we always raise max to buy BTC?
        # "Ponzi" logic: Raise max, pay obligations, buy BTC with rest.
        # But let's stick to the previous logic: Raise to cover obligations + maybe buy BTC?
        # Let's assume aggressive strategy: Always raise max possible to buy BTC, 
        # but first priority is obligations.
        
        # Actually, to keep it simple and robust:
        # 1. Pay obligations from Cash.
        # 2. If Cash < Obligations, raise Capital.
        # 3. If Capital + Cash < Obligations, Sell BTC.
        # 4. If Surplus Capital, Buy BTC.
        
        # Let's model the "Aggressive Accumulation":
        # We try to raise `max_issuance`.
        raised_capital = max_issuance 
        inflows[i] = raised_capital
        
        cash_available = cash_balance[i] + raised_capital
        
        if cash_available >= total_obligations:
            # Pay obligations
            surplus = cash_available - total_obligations
            # Buy BTC with surplus?
            # Let's say we keep a small buffer, but mostly buy BTC.
            # For simplicity: Buy BTC with 90% of surplus.
            btc_to_buy = (surplus * 0.9) / btc_price[i]
            btc_holdings[i] += btc_to_buy
            cash_balance[i] = surplus * 0.1 # Keep 10% as buffer
        else:
            # Shortfall
            shortfall = total_obligations - cash_available
            # Must sell BTC
            btc_needed = shortfall / btc_price[i]
            if btc_needed > btc_holdings[i]:
                # Collapse
                btc_sold[i] = btc_holdings[i]
                btc_holdings[i] = 0
                collapse_month = i
                collapse_reason = "Liquidity Crisis (Ran out of BTC)"
            else:
                btc_holdings[i] -= btc_needed
                btc_sold[i] = btc_needed
                cash_balance[i] = 0

    # Create DataFrame
    df = pd.DataFrame({
        'Month': months,
        'Year': years,
        'BTC_Price': btc_price,
        'MSTR_Price': mstr_stock_price,
        'BTC_Holdings': btc_holdings,
        'Debt': debt_principal,
        'Shares': shares_outstanding,
        'Premium': premium_mult,
        'NAV_Per_Share': nav_per_share,
        'Cash': cash_balance,
        'Inflows': inflows,
        'Outflows': outflows,
        'BTC_Sold': btc_sold
    })
    
    return df, collapse_month, collapse_reason

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="MSTR Simulator 2.0", page_icon="🧨", layout="wide")

st.title("🧨 MSTR Simulator 2.0: The Convertible Debt Edition")
st.markdown("""
**A more accurate simulation of MicroStrategy's leverage mechanics.**
Key improvements:
- **Monthly Resolution**: Catch liquidity crunches that yearly models miss.
- **Convertible Debt Logic**: Debt converts to equity if stock price is high (no maturity wall!).
- **Dynamic Premium**: Premium compresses in bear markets.
""")

# --- Sidebar ---
st.sidebar.header("Configuration")

# Live Data Fetch
if st.sidebar.button("📡 Fetch Live Data"):
    with st.spinner("Fetching from Yahoo Finance..."):
        live_btc, live_mstr, live_shares = fetch_live_data()
        if live_btc:
            st.session_state['btc_price'] = live_btc
            st.session_state['mstr_price'] = live_mstr
            st.session_state['shares'] = live_shares
            st.sidebar.success(f"Fetched! BTC: ${live_btc:,.0f}, MSTR: ${live_mstr:,.2f}")

# Inputs
with st.sidebar.expander("Market Assumptions", expanded=True):
    btc_start = st.number_input("BTC Start Price ($)", value=st.session_state.get('btc_price', 98000.0))
    btc_growth = st.slider("BTC Annual Growth (%)", -50, 100, 15) / 100.0
    base_premium = st.slider("Target Premium (NAV Multiplier)", 0.5, 3.0, 2.0, 0.1)
    dynamic_premium = st.checkbox("Dynamic Premium (Compresses in downturns)", value=True)

with st.sidebar.expander("MSTR Financials", expanded=False):
    btc_holdings = st.number_input("BTC Holdings", value=386000.0) # Nov 2024 approx
    cash_start = st.number_input("Initial Cash ($M)", value=50.0) * 1_000_000
    shares_start = st.number_input("Shares Outstanding", value=st.session_state.get('shares', 225_000_000))
    ops_burn = st.number_input("Annual Ops Burn ($M)", value=100.0) * 1_000_000
    issuance_cap = st.slider("Max Annual Issuance (% of Market Cap)", 0, 100, 25) / 100.0

with st.sidebar.expander("Debt Structure (Advanced)", expanded=False):
    st.caption("Define Convertible Notes")
    # Simplified representation of major tranches
    # 2027, 2028, 2030, 2031, 2032 notes
    # We'll just create a few representative ones
    
    # Tranche 1: 2027/2028
    d1_principal = st.number_input("Tranche 1 Principal ($B)", value=1.0) * 1e9
    d1_year = st.number_input("Tranche 1 Maturity (Year)", value=3) # 2028
    d1_conv = st.number_input("Tranche 1 Conv Price ($)", value=300.0) # Split adjusted approx
    
    # Tranche 2: 2030/2031
    d2_principal = st.number_input("Tranche 2 Principal ($B)", value=2.0) * 1e9
    d2_year = st.number_input("Tranche 2 Maturity (Year)", value=5) # 2030
    d2_conv = st.number_input("Tranche 2 Conv Price ($)", value=400.0)
    
    # Tranche 3: 2032
    d3_principal = st.number_input("Tranche 3 Principal ($B)", value=1.0) * 1e9
    d3_year = st.number_input("Tranche 3 Maturity (Year)", value=7) # 2032
    d3_conv = st.number_input("Tranche 3 Conv Price ($)", value=500.0)

    debts = [
        ConvertibleDebt("Notes 2028", d1_principal, int(d1_year*12), 0.0, d1_conv),
        ConvertibleDebt("Notes 2030", d2_principal, int(d2_year*12), 0.0, d2_conv),
        ConvertibleDebt("Notes 2032", d3_principal, int(d3_year*12), 0.0, d3_conv),
    ]
    
    st.caption("Preferred Stock")
    pref_principal = st.number_input("Preferred Stock Total ($B)", value=0.0) * 1e9 # MSTR has redeemed most? Or new ones? Let's keep 0 default for now unless user adds.
    prefs = [PreferredStock("Series A", pref_principal, 0.0)]

# Simulation
n_years = st.sidebar.slider("Simulation Years", 1, 10, 5)

df, collapse_month, collapse_reason = simulate_mstr_monthly(
    n_months=n_years*12,
    btc_price_start=btc_start,
    btc_growth_annual=btc_growth,
    btc_volatility_annual=0.5, # Not used in deterministic model yet
    btc_holdings_start=btc_holdings,
    cash_start=cash_start,
    shares_start=shares_start,
    convertible_debts=debts,
    preferred_stocks=prefs,
    operating_burn_annual=ops_burn,
    issuance_capacity_pct_annual=issuance_cap,
    base_premium=base_premium,
    dynamic_premium=dynamic_premium
)

# --- Results ---

# Metrics
last_row = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Final BTC Price", f"${last_row['BTC_Price']:,.0f}", delta=f"{(last_row['BTC_Price']/btc_start - 1)*100:.1f}%")
col2.metric("Final MSTR Price", f"${last_row['MSTR_Price']:,.2f}")
col3.metric("Final BTC Holdings", f"{last_row['BTC_Holdings']:,.0f}")
col4.metric("Dilution (Shares)", f"{last_row['Shares']/shares_start:.2f}x")

if collapse_month:
    st.error(f"💥 COLLAPSE in Month {collapse_month} (Year {collapse_month/12:.1f}): {collapse_reason}")
else:
    st.success("✅ SURVIVED! No default or liquidation triggered.")

# Charts (Plotly)
tab1, tab2, tab3 = st.tabs(["Price & Premium", "Balance Sheet", "Cash Flow"])

with tab1:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['Year'], y=df['BTC_Price'], name="BTC Price"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Year'], y=df['MSTR_Price'], name="MSTR Price"), secondary_y=True)
    fig.update_layout(title="BTC vs MSTR Price Action")
    st.plotly_chart(fig, use_container_width=True)
    
    fig_prem = go.Figure()
    fig_prem.add_trace(go.Scatter(x=df['Year'], y=df['Premium'], name="Premium (Multiplier)"))
    fig_prem.update_layout(title="MSTR Premium Over NAV")
    st.plotly_chart(fig_prem, use_container_width=True)

with tab2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['BTC_Holdings'], name="BTC Holdings", fill='tozeroy'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Shares'], name="Shares Outstanding", yaxis="y2"))
    fig.update_layout(
        title="Holdings vs Dilution",
        yaxis=dict(title="BTC Holdings"),
        yaxis2=dict(title="Shares", overlaying="y", side="right")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Debt stack
    fig_debt = go.Figure()
    fig_debt.add_trace(go.Scatter(x=df['Year'], y=df['Debt'], name="Total Debt Principal"))
    fig_debt.update_layout(title="Debt Burden (Decreases as debt converts!)")
    st.plotly_chart(fig_debt, use_container_width=True)

with tab3:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Year'], y=df['Inflows'], name="Capital Inflows (Dilution)"))
    fig.add_trace(go.Bar(x=df['Year'], y=-df['Outflows'], name="Cash Outflows (Ops + Interest)"))
    fig.update_layout(title="Cash Flows", barmode='relative')
    st.plotly_chart(fig, use_container_width=True)
