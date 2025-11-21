# Why "Average Cost" Doesn't Matter (And What Does)

People often focus on MicroStrategy's "Average Cost per Bitcoin" (approx. $66,000 as of late 2025) as a liquidation line. The logic goes: *"If Bitcoin falls below their average cost, they are underwater and will be forced to sell."*

**This is financially incorrect.**

## The Solvency vs. Profitability Distinction

1.  **Profitability (Accounting)**: If $BTC < Average Cost$, MSTR has an *unrealized loss*. This looks bad on an income statement, but it burns **zero cash**.
2.  **Solvency (Survival)**: Solvency is determined by **cash flow** and **contractual obligations**.
    *   **Can they pay the interest?** (Cash Outflows vs. Inflows)
    *   **Must they repay the principal?** (Maturity Walls vs. Conversion)

MicroStrategy's debt is primarily **unsecured convertible notes**.
*   **No Margin Calls**: There is no "Liquidation Price" where a broker forcibly sells their Bitcoin.
*   **No Forced Repayment**: As long as they pay the semi-annual coupons (interest), the principal is not due until the maturity year (e.g., 2027, 2028, 2030).

## The Real Danger: The "Refinancing Wall"

The true risk isn't dipping below $66k. It's arriving at a **Maturity Date** (e.g., 2028) with:
1.  **Stock Price < Conversion Price**: Debt holders demand cash instead of shares.
2.  **No Cash on Hand**: MSTR doesn't have billions in cash.
3.  **Inability to Refinance**: If the market hates MSTR (Premium = 1.0 or less), they can't issue new equity to pay the old debt.

**That** is when they are forced to sell Bitcoin.

## How to Prove It With The Simulator

You can use the simulator to demonstrate that MSTR can survive being "underwater" for years, provided they have liquidity.

### Scenario A: The "Underwater" Survival
*   **BTC Start**: $50,000 (Well below average cost).
*   **BTC Growth**: 0% (Stays flat for 5 years).
*   **Issuance Capacity**: 10% (Market still buys some stock).
*   **Result**: **SURVIVAL**.
    *   *Why?* They have enough cash/inflows to pay the small interest payments. The debt doesn't mature yet. Being "underwater" changes nothing about their daily operations.

### Scenario B: The "Liquidity Crisis" (The Real Killer)
*   **BTC Start**: $50,000.
*   **Issuance Capacity**: 0% (Market panic, premium collapses, no one buys MSTR stock).
*   **Cash Start**: Low ($50M).
*   **Result**: **COLLAPSE**.
    *   *Why?* They run out of cash to pay operating expenses and interest. They are forced to sell BTC to pay bills. This selling drives the price down further.

## Summary for Investors
When people ask "What if BTC drops below their average cost?", the answer is:
> "It doesn't matter. They don't have margin loans. Watch their **Cash Flow** and **Maturity Dates** instead. As long as they can print shares to pay interest, they can survive being underwater indefinitely."
