import streamlit as st
import pandas as pd

# Page layout
st.set_page_config(page_title="LBA ALGO Track System", page_icon="📈", layout="wide")

st.title("LBA ALGO Track System")
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
    # Card ko premium look dene ke liye
    with st.container(border=True):
        raw_symbol = str(row['Stock Symbol']).strip()
        clean_symbol = raw_symbol.split(':')[-1] if ':' in raw_symbol else raw_symbol
        company_name = str(row.get('Company Name', '--'))

        # Header - Thoda chota font use kiya h (Markdown ### ki jagah ####)
        st.markdown(f"##### 🏷️ {raw_symbol}")
        st.caption(f"{company_name}")
        
        # Horizontal Scrolling News Ticker (Marquee)
        st.markdown(f'''
        <marquee scrollamount="4" style="color: #6c757d; font-size: 13px; font-weight: bold; padding: 2px; border-bottom: 1px solid #e0e0e0;">
        🔴 LIVE: Tracking algorithm execution for {clean_symbol}... Watch for technical breakout alerts...
        </marquee>
        ''', unsafe_allow_html=True)

        st.write("") # Thoda space

        # Metrics Layout: 2 Columns me baant diya taaki compact lage
        c1, c2 = st.columns(2)
        
        with c1:
            st.metric(label="Entry Price", value=f"₹{row.get('Entry Price', 0)}")
            st.metric(label="🎯 Target", value=f"₹{row.get('Target Price', 0)}")
            
        with c2:
            # Today's Change ko Delta me daalna (Auto Green/Red)
            try:
                t_change = float(row.get("Today's Change", 0)) * 100
                change_str = f"{t_change:+.2f}%"
            except:
                change_str = "0.00%"
                
            st.metric(label="Live Price", value=f"₹{row.get('Live Price', 0)}", delta=change_str)
            st.metric(label="🔴 SL Level", value=f"₹{row.get('SL Level', 0)}")

        # Live P&L and Status
        pnl_val = format_pct(row.get('Live P&L %', 0))
        status = str(row.get('Status', 'IN TRADE'))
        
        st.divider()
        
        # P&L display based on status
        if status == "TARGET HIT":
            st.success(f"🎯 WIN! P&L: {pnl_val}")
        elif status == "SL HIT":
            st.error(f"🔴 SL HIT! P&L: {pnl_val}")
        else:
            st.info(f"🟡 LIVE P&L: {pnl_val}")

        # Real Buttons for Screener and TradingView
        screener_url = f"https://www.screener.in/company/{clean_symbol}/"
        tv_url = f"https://in.tradingview.com/chart/?symbol={raw_symbol}"
        
        btn1, btn2 = st.columns(2)
        with btn1:
            st.link_button("📊 Screener", screener_url, use_container_width=True)
        with btn2:
            st.link_button("📈 Chart", tv_url, use_container_width=True)

if not df.empty:
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Closed Trades History"])

    with tab1:
        active_df = df[df['Status'].isin(["IN TRADE", "WAITING"])]
        if active_df.empty:
            st.info("Abhi koi active trade nahi hai.")
        else:
            # Size chota karne ke liye ab 4 columns banaye hain (Pehle 3 the)
            cols = st.columns(4)
            for index, row in active_df.iterrows():
                with cols[index % 4]:
                    draw_card(row)

    with tab2:
        history_df = df[df['Status'].isin(["SL HIT", "TARGET HIT"])]
        if history_df.empty:
            st.info("Abhi tak koi bhi trade close nahi hui hai.")
        else:
            # Size chota karne ke liye yahan bhi 4 columns
            cols = st.columns(4)
            history_df = history_df.reset_index(drop=True)
            for index, row in history_df.iterrows():
                with cols[index % 4]:
                    draw_card(row)
else:
    st.warning("⚠️ Google Sheet ekdum khali hai ya URL block ho raha hai.")
