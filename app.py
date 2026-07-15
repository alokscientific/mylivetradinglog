import streamlit as st
import pandas as pd

st.set_page_config(page_title="TRADE LOG", page_icon="📈", layout="wide")

st.title("TRADE LOG")
st.write("**Automated Execution & Faceless Trading Dashboard**")

st.info("Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst. This dashboard strictly tracks personal algorithmic logic. Do not consider this as buy/sell advice.")

SHEET_ID = "1rsrmQMe8hbjGfsAx7039oMPdmqwWC5hHCpEFQSlVH9o"
GID = "1424037063"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=30)
def load_data():
    try:
        data = pd.read_csv(SHEET_CSV_URL)
        data.columns = [str(c).strip() for c in data.columns]
        data = data.dropna(subset=['Stock Symbol'])
        return data
    except Exception as e:
        st.error(f"Google Sheet se connect karne me dikkat aayi: {e}")
        return pd.DataFrame()

df = load_data()

def format_pct(val):
    try:
        if pd.isna(val): return "0.00%"
        if isinstance(val, str) and '%' in val: return val
        return f"{float(val)*100:.2f}%"
    except:
        return "0.00%"

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
            st.metric(label="Live Price", value=f"₹{row.get('Live Price', 0)}")
        with c3:
            pnl_val = format_pct(row.get('Live P&L %', 0))
            st.metric(label="Live P&L", value=pnl_val)

        status = str(row.get('Status', 'IN TRADE'))
        if status == "TARGET HIT":
            st.success("🎯 TARGET HIT")
        elif status == "SL HIT":
            st.error("🔴 SL HIT")
        else:
            st.info("🟡 IN TRADE")

        st.divider()
        screener_url = f"https://www.screener.in/company/{clean_symbol}/"
        tv_url = f"https://in.tradingview.com/chart/?symbol={raw_symbol}"
        st.markdown(f"[📊 Screener Data]({screener_url}) &nbsp; | &nbsp; [📈 TradingView Chart]({tv_url})")

if not df.empty:
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Closed Trades History"])

    with tab1:
        active_df = df[df['Status'].isin(["IN TRADE", "WAITING"])]
        if active_df.empty:
            st.info("Abhi koi active trade nahi hai.")
        else:
            cols = st.columns(3)
            for index, row in active_df.iterrows():
                with cols[index % 3]:
                    draw_card(row)

    with tab2:
        history_df = df[df['Status'].isin(["SL HIT", "TARGET HIT"])]
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
