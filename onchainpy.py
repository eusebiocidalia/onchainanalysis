import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Title
st.title("🔗 On-Chain Metrics Dashboard")

# Instructions
st.markdown("""
This dashboard helps you manually enter and assess on-chain metrics for your favorite cryptocurrencies. 
Color-coded flags will help guide you on potential signals (bullish, neutral, bearish).
""")

# Load initial checklist (can be expanded or replaced with your own Google Sheet integration)
coins = [
    "Bitcoin", "Ethereum", "Solana", "Shiba Inu", "Avalanche",
    "Cardano", "Polkadot", "Chainlink", "Uniswap", "Litecoin",
    "XRP", "Stellar", "Dogecoin", "Wrapped Bitcoin", "Tron",
    "Internet Computer", "Polygon", "Binance Coin", "USD Coin", "Pepe",
    "CRO", "Jupiter", "KAIA"
]

metrics = {
    "Market Capitalization": ("High = Popular, Risk of Overvaluation", "Low = Potential Growth Area"),
    "Realized Capitalization": ("> $100B = High", "< $50B = Low"),
    "Active Addresses": ("> 1M = Strong Network", "< 100k = Weak"),
    "Addresses Holding > X": ("Rising = Confidence", "Dropping = Weak Hands"),
    "Transaction Volume": ("> $10B = Active", "< $1B = Inactive"),
    "Hash Rate": ("High = Secure", "Low = Vulnerable"),
    "Exchange Flows": ("> Inflow = Bearish", "Outflow = Bullish"),
    "Net Unrealized Profit/Loss (NUPL)": (">0.75 = Overheated", "<0.5 = Safer Zone"),
    "Long/Short-Term On-chain Cost Basis": ("Below Price = Bullish", "Above = Risk"),
    "SOPR": (">1 = Profit Taking", "<1 = Capitulation"),
    "MVRV": (">3 = Overvalued", "<1 = Undervalued"),
    "Long-Term Holder MVRV": (">2.5 = Distribution", "<1 = Accumulation"),
    "Short-Term Holder MVRV": (">2 = Caution", "<1 = Opportunity"),
    "MVRV Z-Score": (">7 = Top Zone", "<0 = Undervalued"),
    "Spot Volume": ("> 5B = Volatile", "< 1B = Calm"),
    "Spot Volume Delta": ("> 50% = Shift", "< 10% = Flat"),
    "Percent Balance on Exchanges": (">10% = Risky", "<5% = Safe"),
    "Net Transfer Volume": ("> Outflow = Bullish", "Inflow = Bearish")
}

# Create editable table
data = []
for coin in coins:
    row = {"Coin": coin}
    for metric in metrics:
        row[metric] = ""
    data.append(row)

df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic")

# Show guidance
st.subheader("🧠 Metric Interpretation Guide")
for metric, (high_signal, low_signal) in metrics.items():
    st.markdown(f"**{metric}**: {high_signal} | {low_signal}")

# Summary insights
st.subheader("📊 Summary Insights")
for i, row in edited_df.iterrows():
    coin = row["Coin"]
    insights = []

    try:
        if row["MVRV"] != "" and float(row["MVRV"]) > 3:
            insights.append("⚠️ MVRV is high — overvaluation risk")
        elif row["MVRV"] != "" and float(row["MVRV"]) < 1:
            insights.append("🟢 MVRV is low — may be undervalued")

        if row["SOPR"] != "" and float(row["SOPR"]) > 1.1:
            insights.append("🔺 SOPR high — taking profits")
        elif row["SOPR"] != "" and float(row["SOPR"]) < 1:
            insights.append("🔻 SOPR low — potential bottoming")

        if row["Net Unrealized Profit/Loss (NUPL)"] != "" and float(row["Net Unrealized Profit/Loss (NUPL)"]) > 0.75:
            insights.append("🔥 NUPL is high — market may be overheated")
        elif row["Net Unrealized Profit/Loss (NUPL)"] != "" and float(row["Net Unrealized Profit/Loss (NUPL)"]) < 0.5:
            insights.append("🟢 NUPL is moderate — safer zone")

        if row["MVRV Z-Score"] != "" and float(row["MVRV Z-Score"]) > 7:
            insights.append("🚨 MVRV Z-Score > 7 — strong top signal")
        elif row["MVRV Z-Score"] != "" and float(row["MVRV Z-Score"]) < 0:
            insights.append("🟢 MVRV Z-Score < 0 — likely undervalued")

    except ValueError:
        continue

    if insights:
        st.markdown(f"**{coin}**")
        for ins in insights:
            st.write(ins)

# Download section
st.subheader("📥 Download Your Data")
st.download_button(
    label="Download CSV",
    data=edited_df.to_csv(index=False).encode('utf-8'),
    file_name="onchain_metrics_snapshot.csv",
    mime="text/csv"
)

# Google Sheets Upload (requires credentials.json)
st.subheader("📤 Save to Google Sheets")
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(credentials)
    sheet = client.create("OnChain_Metrics_Snapshot")
    worksheet = sheet.get_worksheet(0)
    worksheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
    st.success("Successfully uploaded to Google Sheets!")
except Exception as e:
    st.warning("Google Sheets upload failed. Make sure 'credentials.json' exists and has access.")
    st.text(str(e))
