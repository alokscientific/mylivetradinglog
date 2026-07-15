import streamlit as st
import pandas as pd

# Page layout & New Name
st.set_page_config(page_title="TRADE LOG SYSTEM", page_icon="⚡", layout="wide")

# Custom CSS for Robotic/Professional Look & Blue Outline
st.markdown("""
<style>
/* Robotic Font Setup */
html, body, [class*="st-"] {
    font-family: 'Courier New', Courier, monospace !important;
}

/* Blue Outline and Compact Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 2px solid #00E5FF !important; /* Neon Blue Outline */
    border-radius: 6px !important;
    padding: 6px !important;
    background-color: rgba(0, 25, 50, 0.05); /* Very light blue tint in background */
}

/* Text Visibility Improvements */
div[data-testid="stMetricValue"] {
    font-size: 1.3rem !important; 
    font-weight: 900 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    font-weight: 900 !important;
    color: #0056b3 !important; /* Dark Blue for high visibility */
}

/* Dynamic News Ticker Style */
.news-ticker {
    background-color: #001f3f;
    color: #00E5FF;
    font-size: 12px;
    font-weight: bold;
    padding: 4px;
    border: 1px solid #00E5FF;
    border-radius: 4px;
    margin-top: -5px;
    margin-bottom: 10px;
}

/* Compact Info Bar */
.info-bar {
    font-size: 11px;
    font-weight: 900;
    color: #333;
    background-color: #e9ecef;
    padding: 4px;
    border-radius: 3px;
    text-align: center;
    border: 1px solid #ccc;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ TRADE LOG SYSTEM")
st.write("**Track and Trade**")

st.info("Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst. This dashboard strictly tracks personal algorithmic logic.")

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
        st.error(f"Error fetching data: {e}")
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
        company_name = str(row.get('Company Name', '--'))[:15] # Naam bada ho toh cut ho jayega taaki line break na ho

        # Live variables for Ticker
        live_p = row.get('Live Price', 0)
        tgt = row.get('Target Price', 0)
        sl = row.get('SL Level', 0)
        entry_p = row.get('Entry Price', 0)
        
        # Header (Very compact)
        st.markdown(f"**🤖 {raw_symbol}** | `{company_name}`")
        
        # Dynamic Scrolling Ticker (Ab har stock ka real data chalega)
        ticker_msg = f"SYSTEM ALERT // ALGO TRACKING {clean_symbol} // LIVE PRICE: ₹{live_p} // TARGET LOCK: ₹{tgt} // SL PROTECTION: ₹{sl} //"
        st.markdown(f'<marquee class="news-ticker" scrollamount="4">{ticker_msg}</marquee>', unsafe_allow_html=True)

        # Main Metrics
        c1, c2 = st.columns(2)
        with c1:
            try:
                t_change = float(row.get("Today's Change", 0)) * 100
                change_str = f"{t_change:+.2f}%"
            except:
                change_str = "0.00%"
            st.metric(label="LIVE PRICE", value=f"₹{live_p}", delta=change_str)
            
        with c2:
            pnl_val = format_pct(row.get('Live P&L %', 0))
            st.metric(label="LIVE P&L", value=pnl_val)

        # Compact Info Bar (Entry, Target, SL in one single line to save vertical space)
        st.markdown(f"<div class='info-bar'>ENTRY: ₹{entry_p} | TGT: ₹{tgt} | SL: ₹{sl}</div>", unsafe_allow_html=True)

        # Status Display
        status = str(row.get('Status', 'IN TRADE'))
        if status == "TARGET HIT":
            st.markdown("<div style='color:#00ff00; font-weight:900; font-size:14px; text-align:center; background:#003300; padding:2px; border-radius:3px;'>🎯 WIN [TARGET HIT]</div>", unsafe_allow_html=True)
        elif status == "SL HIT":
            st.markdown("<div style='color:#ff0000; font-weight:900; font-size:14px; text-align:center; background:#330000; padding:2px; border-radius:3px;'>🔴 LOSS [SL HIT]</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#ffaa00; font-weight:900; font-size:14px; text-align:center; background:#332200; padding:2px; border-radius:3px;'>⚡ SYSTEM ACTIVE</div>", unsafe_allow_html=True)
            
        st.write("") # Micro space
        
        # Tiny Action Buttons
        btn1, btn2 = st.columns(2)
        with btn1:
            st.link_button("Screener", f"https://www.screener.in/company/{clean_symbol}/", use_container_width=True)
        with btn2:
            st.link_button("Chart", f"https://in.tradingview.com/chart/?symbol={raw_symbol}", use_container_width=True)

if not df.empty:
    tab1, tab2 = st.tabs(["📊 ACTIVE TRADES", "📜 CLOSED TRADES"])

    with tab1:
        active_df = df[df['Status'].isin(["IN TRADE", "WAITING"])]
        if active_df.empty:
            st.info("No active trades found.")
        else:
            # 5 Columns ki wajah se cards patle aur chote ho jayenge (No extra scrolling)
            cols = st.columns(5)
            for index, row in active_df.iterrows():
                with cols[index % 5]:
                    draw_card(row)

    with tab2:
        history_df = df[df['Status'].isin(["SL HIT", "TARGET HIT"])]
        if history_df.empty:
            st.info("No closed trades found.")
        else:
            cols = st.columns(5)
            history_df = history_df.reset_index(drop=True)
            for index, row in history_df.iterrows():
                with cols[index % 5]:
                    draw_card(row)
else:
    st.warning("⚠️ Data source is empty or unreachable.")
