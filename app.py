import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_javascript import st_javascript


# -----------------------------
# Core simulation logic
# -----------------------------
def simulate_mstr_ponzi(
    start_year: int,
    n_years: int,
    btc_price_start: float,
    btc_annual_growth: float,
    btc_holdings_start: float,
    debt_nominal_start: float,
    preferred_nominal_start: float,
    preferred_coupon: float,
    debt_interest_rate: float,
    operating_cash_burn: float,
    issuance_capacity_pct: float,
    equity_premium_lambda: float,
    include_maturity_wall: bool,
    maturity_schedule: dict,
):
    """
    Very simplified yearly model of MSTR/Strategy as a levered BTC vehicle
    with Ponzi-like funding dynamics.

    State variables per year:
      - BTC price
      - BTC holdings
      - cash balance
      - asset value, senior claims, NAV (equity)
      - capital inflows vs cash obligations
    """

    years = np.arange(start_year, start_year + n_years)

    # Allocate arrays
    btc_price = np.zeros(n_years)
    btc_holdings = np.zeros(n_years)
    cash_balance = np.zeros(n_years)

    asset_value = np.zeros(n_years)
    senior_claims = np.zeros(n_years)
    nav_equity = np.zeros(n_years)
    market_cap = np.zeros(n_years)

    obligations = np.zeros(n_years)
    inflows = np.zeros(n_years)
    funding_gap = np.zeros(n_years)
    btc_sold = np.zeros(n_years)

    # Initial conditions
    btc_price[0] = btc_price_start
    btc_holdings[0] = btc_holdings_start
    cash_balance[0] = 0.0

    debt_nominal = debt_nominal_start
    preferred_nominal = preferred_nominal_start

    collapse_year = None
    collapse_reason = None

    for i, year in enumerate(years):
        # --- Update BTC price deterministically ---
        if i > 0:
            btc_price[i] = btc_price[i - 1] * (1.0 + btc_annual_growth)

            # carry forward state
            btc_holdings[i] = btc_holdings[i - 1]
            cash_balance[i] = cash_balance[i - 1]
        else:
            # first year already initialized
            pass

        # --- Compute asset side and senior claims ---
        asset_value[i] = btc_price[i] * btc_holdings[i] + cash_balance[i]
        senior_claims[i] = debt_nominal + preferred_nominal

        nav_equity[i] = max(asset_value[i] - senior_claims[i], 0.0)

        # If equity is already wiped, we record collapse and stop
        if nav_equity[i] <= 0 and collapse_year is None:
            collapse_year = int(year)
            collapse_reason = "Equity NAV <= 0 (assets < senior claims)"
            # No need to simulate further; fill the rest with NaNs
            for j in range(i + 1, n_years):
                btc_price[j] = np.nan
                btc_holdings[j] = np.nan
                cash_balance[j] = np.nan
                asset_value[j] = np.nan
                senior_claims[j] = np.nan
                nav_equity[j] = np.nan
                market_cap[j] = np.nan
                obligations[j] = np.nan
                inflows[j] = np.nan
                funding_gap[j] = np.nan
                btc_sold[j] = np.nan
            break

        # --- Compute market cap from NAV and equity premium ---
        if equity_premium_lambda <= 0 or nav_equity[i] <= 0:
            market_cap[i] = 0.0
        else:
            market_cap[i] = nav_equity[i] * equity_premium_lambda

        # --- Compute yearly obligations ---
        interest_debt = debt_nominal * debt_interest_rate
        pref_div = preferred_nominal * preferred_coupon
        op_exp = operating_cash_burn

        maturity_principal = 0.0
        if include_maturity_wall and (year in maturity_schedule):
            maturity_principal = maturity_schedule[year]

        obligations[i] = interest_debt + pref_div + op_exp + maturity_principal

        # --- Capital inflows: new equity/preferred/debt issuance ---
        # Limit: issuance_capacity_pct * market_cap
        issuance_limit = issuance_capacity_pct * market_cap[i]

        # How much we actually need (after existing cash)
        required_funding = max(obligations[i] - cash_balance[i], 0.0)

        inflows[i] = min(issuance_limit, required_funding)

        # Update cash with inflows, then pay obligations as far as possible
        cash_after_inflows = cash_balance[i] + inflows[i]

        if cash_after_inflows >= obligations[i]:
            # We can pay everything out of cash + new capital; no BTC sale needed
            cash_balance[i] = cash_after_inflows - obligations[i]
            funding_gap[i] = 0.0
            btc_sold[i] = 0.0

        else:
            # We have a shortfall and must either sell BTC or default
            gap = obligations[i] - cash_after_inflows
            funding_gap[i] = gap

            # BTC sale required to plug the gap
            if btc_price[i] > 0:
                required_btc_sale = gap / btc_price[i]
            else:
                required_btc_sale = np.inf

            if required_btc_sale <= btc_holdings[i]:
                # Sell BTC to plug the hole
                btc_holdings[i] -= required_btc_sale
                btc_sold[i] = required_btc_sale
                cash_balance[i] = 0.0
            else:
                # Not enough BTC to sell -> collapse
                collapse_year = int(year)
                collapse_reason = (
                    "Funding gap could not be filled even after selling all BTC"
                )
                # Mark end-state BTC/cash
                btc_sold[i] = btc_holdings[i]
                btc_holdings[i] = 0.0
                cash_balance[i] = 0.0

                # Fill future years with NaNs
                for j in range(i + 1, n_years):
                    btc_price[j] = np.nan
                    btc_holdings[j] = np.nan
                    cash_balance[j] = np.nan
                    asset_value[j] = np.nan
                    senior_claims[j] = np.nan
                    nav_equity[j] = np.nan
                    market_cap[j] = np.nan
                    obligations[j] = np.nan
                    inflows[j] = np.nan
                    funding_gap[j] = np.nan
                    btc_sold[j] = np.nan
                break

        # Conceptually, if a maturity_principal was due and we paid it,
        # we could assume the company refinances into new debt of the same size,
        # so debt_nominal stays constant.
        # If you want to model actual deleveraging or failed refinancing,
        # you'd modify debt_nominal here based on cash/inflows.

    # Build dataframe for analysis/plotting
    df = pd.DataFrame(
        {
            "Year": years,
            "BTC_Price": btc_price,
            "BTC_Holdings": btc_holdings,
            "Cash_Balance": cash_balance,
            "Asset_Value": asset_value,
            "Senior_Claims": senior_claims,
            "NAV_Equity": nav_equity,
            "Market_Cap": market_cap,
            "Obligations": obligations,
            "Capital_Inflows": inflows,
            "Funding_Gap": funding_gap,
            "BTC_Sold": btc_sold,
        }
    )

    return df, collapse_year, collapse_reason


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="MSTR Goes Boom: When Does MicroStrategy's Bitcoin Bet Collapse?",
    page_icon="🧨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "An interactive model exploring MicroStrategy/Strategy's leveraged Bitcoin capital structure through a Ponzi-lens."
    }
)

# Inject Open Graph meta tags for better social media previews
st_javascript("""
    const metaTags = [
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: 'https://microstrategy-goes-boom-neydsqr7vhwwa2wzgrdksj.streamlit.app/' },
        { property: 'og:title', content: 'MSTR Goes Boom: When Does MicroStrategy\\'s Bitcoin Bet Collapse?' },
        { property: 'og:description', content: '🧨 Interactive simulation: Test different scenarios to see when (or if) MicroStrategy\\'s leveraged Bitcoin strategy collapses. Bull or Bear - Run your own scenarios!' },
        { property: 'og:image', content: 'https://raw.githubusercontent.com/konstantinosfotiou/microstrategy-goes-boom/main/preview.png' },
        { property: 'og:site_name', content: 'MSTR Goes Boom Simulator' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: 'MSTR Goes Boom: When Does MicroStrategy\\'s Bitcoin Bet Collapse?' },
        { name: 'twitter:description', content: '🧨 Interactive simulation: Test different scenarios to see when (or if) MicroStrategy\\'s leveraged Bitcoin strategy collapses!' },
        { name: 'twitter:image', content: 'https://raw.githubusercontent.com/konstantinosfotiou/microstrategy-goes-boom/main/preview.png' }
    ];
    
    metaTags.forEach(tag => {
        const meta = document.createElement('meta');
        if (tag.property) meta.setAttribute('property', tag.property);
        if (tag.name) meta.setAttribute('name', tag.name);
        meta.setAttribute('content', tag.content);
        document.head.appendChild(meta);
    });
""")

st.title("🧨 MSTR Goes Boom: When Does MicroStrategy's Bitcoin Bet Collapse?")

st.markdown(
    """
**Will MicroStrategy's leveraged Bitcoin bet survive, or will it go boom?** 💥

This interactive simulator models MSTR/Strategy's capital structure through a *Ponzi-lens*: 
the system survives as long as **new capital inflows** plus cash and BTC sales can meet 
**cash obligations** (opex, coupons, debt maturities).

🎮 **Play with the scenarios** on the left to see what breaks the system:
- Bull market with Bitcoin mooning? 🚀
- Bear market with BTC stagnation? 🐻
- Hard crash with funding frozen? 💀

⚠️ **Disclaimer:** This is a **toy model** – not investment advice, not a forecast. 
It ignores tons of real-world nuance. Use it as an intuition-building sandbox.
"""
)

# Sidebar – scenario selection
st.sidebar.header("Scenario & Parameters")

scenario = st.sidebar.selectbox(
    "Scenario preset",
    [
        "Custom",
        "Bull (BTC moon)",
        "Base (modest BTC)",
        "Bear (BTC stagnation)",
        "Stress (slow bleed)",
        "Collapse ~2030 (medium-hard bear)",
        "Collapse ~2028 (hard crash)",
    ],
)

# Default parameters
default_btc_price = 105_000.0
default_btc_holdings = 640_000.0
default_debt_nominal = 8_000_000_000.0
default_pref_nominal = 3_600_000_000.0

# Scenario-based defaults (can still be overridden via UI)
default_growth = 0.10
default_operating_burn = 500_000_000.0
default_pref_nominal = default_pref_nominal
default_pref_coupon_pct = 9.0
default_debt_nominal = default_debt_nominal
default_issuance_capacity = 0.30
default_lambda = 1.2

if scenario == "Bull (BTC moon)":
    default_growth = 0.20
    default_operating_burn = 400_000_000.0
    default_pref_nominal = 3_000_000_000.0
    default_pref_coupon_pct = 8.0
    default_debt_nominal = 7_000_000_000.0
    default_issuance_capacity = 0.50
    default_lambda = 1.5
elif scenario == "Base (modest BTC)":
    default_growth = 0.08
    default_operating_burn = 500_000_000.0
    default_pref_nominal = 3_600_000_000.0
    default_pref_coupon_pct = 9.0
    default_debt_nominal = 8_000_000_000.0
    default_issuance_capacity = 0.30
    default_lambda = 1.2
elif scenario == "Bear (BTC stagnation)":
    default_growth = 0.00
    default_operating_burn = 600_000_000.0
    default_pref_nominal = 4_500_000_000.0
    default_pref_coupon_pct = 10.0
    default_debt_nominal = 8_500_000_000.0
    default_issuance_capacity = 0.20
    default_lambda = 1.0
elif scenario == "Stress (slow bleed)":
    # Flat BTC, premium gone, structure eats BTC but may not collapse immediately
    default_growth = 0.00
    default_operating_burn = 700_000_000.0
    default_pref_nominal = 5_000_000_000.0
    default_pref_coupon_pct = 10.0
    default_debt_nominal = 8_000_000_000.0
    default_issuance_capacity = 0.15
    default_lambda = 1.0
elif scenario == "Collapse ~2030 (medium-hard bear)":
    # BTC decays, obligations heavy, issuance constrained – collapse likely near 2030 wall
    default_growth = -0.20
    default_operating_burn = 900_000_000.0
    default_pref_nominal = 9_000_000_000.0
    default_pref_coupon_pct = 12.0
    default_debt_nominal = 8_000_000_000.0
    default_issuance_capacity = 0.05
    default_lambda = 0.7
elif scenario == "Collapse ~2028 (hard crash)":
    # Aggressive bear and funding shut – early collapse around first big maturities
    default_growth = -0.30
    default_operating_burn = 1_300_000_000.0
    default_pref_nominal = 11_000_000_000.0
    default_pref_coupon_pct = 16.0
    default_debt_nominal = 8_000_000_000.0
    default_issuance_capacity = 0.02
    default_lambda = 0.5

start_year = st.sidebar.number_input("Start year", value=2025, step=1)
n_years = st.sidebar.slider("Years to simulate", min_value=3, max_value=20, value=10)

btc_price_start = st.sidebar.number_input(
    "Initial BTC price (USD)", value=default_btc_price, step=5_000.0, min_value=1.0
)
btc_annual_growth_pct = st.sidebar.number_input(
    "BTC annual growth rate (%)", value=default_growth * 100, step=5.0, min_value=-100.0
)
btc_annual_growth = btc_annual_growth_pct / 100.0

btc_holdings_start = st.sidebar.number_input(
    "Initial BTC holdings (coins)",
    value=float(default_btc_holdings),
    step=20_000.0,
    min_value=0.0,
)

debt_nominal_start = st.sidebar.number_input(
    "Senior debt nominal (USD)",
    value=float(default_debt_nominal),
    step=500_000_000.0,
    min_value=0.0,
)

preferred_nominal_start = st.sidebar.number_input(
    "Preferred nominal (USD)",
    value=float(default_pref_nominal),
    step=200_000_000.0,
    min_value=0.0,
)

preferred_coupon_pct = st.sidebar.number_input(
    "Preferred coupon rate (%)",
    value=default_pref_coupon_pct,
    step=0.5,
    min_value=0.0,
)
preferred_coupon = preferred_coupon_pct / 100.0

debt_interest_pct = st.sidebar.number_input(
    "Average debt interest rate (%)", value=1.0, step=0.25, min_value=0.0
)
debt_interest_rate = debt_interest_pct / 100.0

operating_cash_burn = st.sidebar.number_input(
    "Operating cash burn per year (USD)",
    value=default_operating_burn,
    step=50_000_000.0,
    min_value=0.0,
)

issuance_capacity_pct = st.sidebar.slider(
    "Max new capital per year (% of equity market cap)",
    min_value=0.0,
    max_value=1.0,
    value=float(default_issuance_capacity),
    step=0.05,
)

equity_premium_lambda = st.sidebar.number_input(
    "Equity premium multiple over NAV (λ)",
    value=default_lambda,
    step=0.1,
    min_value=0.0,
)

include_maturity_wall = st.sidebar.checkbox(
    "Include debt maturity wall (lump-sum principal years)", value=True
)

st.sidebar.markdown("**Maturity schedule (hard-coded, editable in code):**")
st.sidebar.markdown(
    """
- 2028: $2.0B
- 2030: $2.0B
"""
)

# Hard-coded maturity schedule for now; you can expose this to the UI later.
maturity_schedule = {2028: 2_000_000_000.0, 2030: 2_000_000_000.0}

# Run simulation
df, collapse_year, collapse_reason = simulate_mstr_ponzi(
    start_year=start_year,
    n_years=n_years,
    btc_price_start=btc_price_start,
    btc_annual_growth=btc_annual_growth,
    btc_holdings_start=btc_holdings_start,
    debt_nominal_start=debt_nominal_start,
    preferred_nominal_start=preferred_nominal_start,
    preferred_coupon=preferred_coupon,
    debt_interest_rate=debt_interest_rate,
    operating_cash_burn=operating_cash_burn,
    issuance_capacity_pct=issuance_capacity_pct,
    equity_premium_lambda=equity_premium_lambda,
    include_maturity_wall=include_maturity_wall,
    maturity_schedule=maturity_schedule,
)

# -----------------------------
# Output & charts
# -----------------------------
st.subheader("Simulation Summary")

# Use the last valid row (in case of early collapse with NaNs afterwards)
last_valid_idx = df["BTC_Price"].last_valid_index()
last_row = df.loc[last_valid_idx] if last_valid_idx is not None else df.iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Last BTC price", f"${last_row['BTC_Price']:,.0f}")
with col2:
    st.metric("Last BTC holdings", f"{last_row['BTC_Holdings']:,.0f} BTC")
with col3:
    st.metric("Last NAV (Equity)", f"${last_row['NAV_Equity']:,.0f}")

if collapse_year is not None:
    st.error(f"🧨 Model collapse year: {collapse_year} – {collapse_reason}")
    st.markdown(
        """
**Interpretation:** under this parameter set, the structure can no longer roll its
obligations with new capital and available BTC. Either asset value has fallen below
senior claims, or even liquidating all BTC is insufficient to plug the funding gap
in that year. In a real-world analogue, that is the zone of distressed refinance,
forced BTC liquidation, or formal restructuring where common equity is at severe risk.
        """
    )
else:
    st.success("No model collapse within the simulated horizon.")
    st.markdown(
        """
**Interpretation:** within the simulated window, new capital plus BTC sales are
sufficient to meet cash obligations. That does *not* mean the structure is safe,
but that under these assumptions it can continue to roll forward without a hard
funding stop.
        """
    )

st.dataframe(df.set_index("Year"))

# Plot 1: BTC price and BTC holdings
st.subheader("BTC Price and Holdings Over Time")
fig1, ax1 = plt.subplots()
ax1.plot(df["Year"], df["BTC_Price"], label="BTC Price (USD)")
ax1.set_xlabel("Year")
ax1.set_ylabel("BTC Price (USD)")
ax1.grid(True)
ax1_2 = ax1.twinx()
ax1_2.plot(df["Year"], df["BTC_Holdings"], linestyle="--", label="BTC Holdings (coins)")
ax1_2.set_ylabel("BTC Holdings")
fig1.legend(loc="upper left")
st.pyplot(fig1)

# Plot 2: Asset value vs senior claims vs NAV
st.subheader("Balance Sheet: Asset Value vs Senior Claims vs NAV")
fig2, ax2 = plt.subplots()
ax2.plot(df["Year"], df["Asset_Value"], label="Asset Value")
ax2.plot(df["Year"], df["Senior_Claims"], label="Senior Claims")
ax2.plot(df["Year"], df["NAV_Equity"], label="NAV (Equity)")
ax2.set_xlabel("Year")
ax2.set_ylabel("USD")
ax2.grid(True)
ax2.legend()
if collapse_year is not None:
    ax2.axvline(collapse_year, linestyle="--", linewidth=1)
    ax2.text(
        collapse_year,
        max(df["Asset_Value"].max(), df["Senior_Claims"].max()) * 0.9,
        "Collapse",
        rotation=90,
        verticalalignment="top",
    )
st.pyplot(fig2)

# Plot 3: Obligations vs Capital Inflows
st.subheader("Cash Obligations vs Capital Inflows")
fig3, ax3 = plt.subplots()
ax3.plot(df["Year"], df["Obligations"], label="Cash Obligations")
ax3.plot(df["Year"], df["Capital_Inflows"], label="Capital Inflows")
ax3.set_xlabel("Year")
ax3.set_ylabel("USD per year")
ax3.grid(True)
ax3.legend()
if collapse_year is not None:
    ax3.axvline(collapse_year, linestyle="--", linewidth=1)
st.pyplot(fig3)

# Plot 4: Funding gap and BTC sold
st.subheader("Funding Gap and BTC Sold")
fig4, ax4 = plt.subplots()
ax4.plot(df["Year"], df["Funding_Gap"], label="Funding Gap")
ax4.set_xlabel("Year")
ax4.set_ylabel("USD")
ax4.grid(True)
ax4_2 = ax4.twinx()
ax4_2.plot(df["Year"], df["BTC_Sold"], linestyle="--", label="BTC Sold (coins)")
ax4_2.set_ylabel("BTC Sold (coins)")
fig4.legend(loc="upper left")
if collapse_year is not None:
    ax4.axvline(collapse_year, linestyle="--", linewidth=1)
st.pyplot(fig4)

st.markdown(
    """
### How to interpret this (through a collapse lens)

- **Survival region:** as long as *Capital Inflows ≥ Obligations* and BTC holdings remain large,
  the structure can keep rolling – it can always find enough new money and/or sell a manageable
  amount of BTC to meet coupons, opex, and maturities.
- **Stress region:** when Obligations start to approach or exceed Inflows, you’ll see
  **Funding_Gap > 0** and **BTC_Sold > 0** – the structure is forced to eat into its BTC stack.
  If this persists and BTC does not recover, NAV compresses and senior claims dominate.
- **Collapse:** when equity NAV goes to zero *or* you hit a year where even selling all BTC cannot
  plug the gap, the model flags a **collapse year**. In economic terms that is the point where
  some combination of:
  - distressed refinancing,
  - massively dilutive rescue equity,
  - or formal restructuring
  would be needed, with common equity at high risk of being impaired or wiped.

By toggling scenarios and tweaking BTC growth, preferred coupons, issuance capacity, and the
maturity wall, you can explore which combinations of variables make the system surprisingly
robust vs. clearly fragile.
    """
)
