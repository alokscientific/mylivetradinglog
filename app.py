import streamlit as st
import pandas as pd

# Page layout aur config set kar rahe hain
st.set_page_config(page_title="LBA ALGO Track System", page_icon="📈", layout="wide")

# Dashboard ka Title aur Subtitle
st.title("LBA ALGO Track System")
st.write("**Automated Execution & Faceless Trading Dashboard**")

# SEBI Disclaimer Box
st.info("Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst. This dashboard strictly tracks personal algorithmic logic. Do not consider this as buy/sell advice.")

# Aapki Google Sheet ka Live CSV Export URL (ID aur GID ke sath)
SHEET_ID = "1rsrmQMe8hbjGfsAx7039oMPdmqwWC5hHCpEFQSlVH9o"
GID = "1424037063"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# --- INVESTMENT CONSTANTS ---
TOTAL_PORTFOLIO_CAPITAL = 1000000  # 10 Lakh base capital
INVESTMENT_PER_TRADE = 100000      # 1 Lakh per trade

@st.cache_data(ttl=30)  # Har 30 second me data auto-refresh hoga
def load_data():
    try:
        data = pd.read_csv(SHEET_CSV_URL)
        data.columns = [str(c).strip() for c in data.columns]
        # Khali rows ko hata denge
        data = data.dropna(subset=['Stock Symbol'])
        return data
    except Exception as e:
        st.error(f"Google Sheet se connect karne me dikkat aayi: {e}")
        return pd.DataFrame()

df = load_data()

def format_pct(val):
    try:
        if pd.isna(val) or str(val).strip() in ["", "#VALUE!"]: return "0.00%"
        if isinstance(val, str) and '%' in val: return val
        return f"{float(val)*100:.2f}%"
    except:
        return "0.00%"

def safe_float(val):
    try:
        if pd.isna(val) or str(val).strip() in ["", "#VALUE!"]: return 0.0
        return float(str(val).replace('%', '').replace(',', ''))
    except:
        return 0.0

# --- CARD BANANE KA FUNCTION ---
def draw_card(row):
    with st.container(border=True):
        raw_symbol = str(row['Stock Symbol']).strip()
        clean_symbol = raw_symbol.split(':')[-1] if ':' in raw_symbol else raw_symbol
        company_name = str(row.get('Company Name', '--'))

        st.markdown(f"#### 🏷️ {raw_symbol}")
        st.caption(f"{company_name}")
        st.divider() 

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="Entry Price", value=f"₹{row.get('Entry Price', 0)}")
        with c2:
            # Handle Blank/Error cells safely
            live_p = row.get('Live Price', 0)
            if pd.isna(live_p) or str(live_p).strip() in ["", "#VALUE!"]:
                live_p = "--"
            st.metric(label="Live Price", value=f"₹{live_p}")
        with c3:
            pnl_val = format_pct(row.get('Live P&L %', 0))
            st.metric(label="Live P&L", value=pnl_val)

        status = str(row.get('Status', 'IN TRADE')).strip().upper()
        if status == "TARGET HIT":
            st.success("🎯 TARGET HIT")
        elif status == "SL HIT":
            st.error("🔴 SL HIT")
        elif status == "TRAIL EXIT":
            st.warning("🛡️ TRAIL EXIT")
        elif status == "REPLACED":
            st.secondary("🔄 REPLACED")
        elif status == "WAITING":
            st.info("⏳ WAITING")
        else:
            st.info("🟡 IN TRADE")

        st.divider()
        screener_url = f"https://www.screener.in/company/{clean_symbol}/"
        tv_url = f"https://in.tradingview.com/chart/?symbol={raw_symbol}"
        st.markdown(f"[📊 Screener Data]({screener_url}) &nbsp; | &nbsp; [📈 TradingView Chart]({tv_url})")


if not df.empty:
    
    # --- 10 LAKH PORTFOLIO P&L CALCULATION (FIXED HISTORY) ---
    closed_trades = df[df['Status'].isin(["SL HIT", "TARGET HIT", "TRAIL EXIT", "REPLACED"])]
    total_realized_pnl = 0.0
    
    for _, row in closed_trades.iterrows():
        entry = safe_float(row.get('Entry Price', 0))
        status = str(row.get('Status', '')).strip().upper()
        
        # Exact calculation using fixed exit levels (Live price ignore karega)
        exit_p = 0.0
        if status == "TARGET HIT": exit_p = safe_float(row.get('Target Price', 0))
        elif status == "SL HIT": exit_p = safe_float(row.get('SL Level', 0))
        elif status == "TRAIL EXIT": exit_p = safe_float(row.get('Trailed SL', 0))
        
        if exit_p == 0: exit_p = safe_float(row.get('Live Price', 0))
        
        if entry > 0 and exit_p > 0:
            pct_gain = (exit_p - entry) / entry
            pnl_rs = pct_gain * INVESTMENT_PER_TRADE
            total_realized_pnl += pnl_rs

    portfolio_pct = (total_realized_pnl / TOTAL_PORTFOLIO_CAPITAL) * 100
    
    # Simple Portfolio Header
    st.subheader("💼 Portfolio Snapshot (₹10 Lakh Capital)")
    pnl_color = "green" if total_realized_pnl >= 0 else "red"
    st.markdown(f"**Total Realized P&L:** :{pnl_color}[₹{total_realized_pnl:,.2f} ({portfolio_pct:+.2f}%)]")
    st.divider()

    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Closed Trades History"])

    with tab1:
        active_df = df[df['Status'].isin(["IN TRADE", "WAITING"])]
        if active_df.empty:
            st.info("Abhi koi active trade nahi hai.")
        else:
            cols = st.columns(3)
            active_df = active_df.reset_index(drop=True)
            for index, row in active_df.iterrows():
                with cols[index % 3]:
                    draw_card(row)

    with tab2:
        history_df = closed_trades
        if history_df.empty:
            st.info("Abhi tak koi bhi trade close nahi hui hai.")
        else:
            cols = st.columns(3)
            history_df = history_df.reset_index(drop=True)
            for index, row in history_df.iterrows():
                with cols[index % 3]:
                    draw_card(row)
else:
    st.warning("⚠️ Google Sheet ekdum khali hai ya URL block ho raha hai.")
