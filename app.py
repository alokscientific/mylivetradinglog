import streamlit as st
import pandas as pd

# Page config - Clean title and icon
st.set_page_config(page_title="TRADE LOG SYSTEM", page_icon="📊", layout="wide")

# Modern, Professional CSS (Zerodha/Sensibull style)
st.markdown("""
<style>
/* Clean Metric Values */
div[data-testid="stMetricValue"] {
    font-size: 1.1rem !important; 
    font-weight: 600 !important;
    color: #1e293b !important;
}
/* Subdued Metric Labels */
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
/* Subtle, professional card borders */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    background-color: #ffffff;
    padding: 0.5rem !important;
}
/* Status Badges */
.badge-active {
    background-color: #f1f5f9;
    color: #0284c7;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-win {
    background-color: #dcfce7;
    color: #166534;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-loss {
    background-color: #fee2e2;
    color: #991b1b;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
/* Clean Context Data Row */
.context-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #475569;
    background-color: #f8fafc;
    border-top: 1px solid #f1f5f9;
    border-bottom: 1px solid #f1f5f9;
    padding: 6px 4px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("### 📊 TRADE LOG SYSTEM")
st.caption("**Track and Trade | Algorithmic Execution Dashboard**")
st.divider()

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
        company_name = str(row.get('Company Name', '--'))[:20]

        status = str(row.get('Status', 'IN TRADE'))
        
        # Badge logic
        if status == "TARGET HIT":
            badge = "<span class='badge-win'>WIN</span>"
        elif status == "SL HIT":
            badge = "<span class='badge-loss'>LOSS</span>"
        else:
            badge = "<span class='badge-active'>ACTIVE</span>"

        # Card Header: Symbol on left, Badge on right
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #0f172a;">{clean_symbol}</div>
            <div>{badge}</div>
        </div>
        <div style="font-size: 0.7rem; color: #94a3b8; margin-bottom: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{company_name}</div>
        """, unsafe_allow_html=True)

        # Core Metrics: Live Price with Delta and P&L
        live_p = row.get('Live Price', 0)
        pnl_val = format_pct(row.get('Live P&L %', 0))
        
        try:
            t_change = float(row.get("Today's Change", 0)) * 100
            change_str = f"{t_change:+.2f}%"
        except:
            change_str = "0.00%"

        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="LIVE PRICE", value=f"₹{live_p}", delta=change_str)
        with c2:
            st.metric(label="LIVE P&L", value=pnl_val)

        # Professional Context Bar for Levels
        entry_p = row.get('Entry Price', 0)
        tgt = row.get('Target Price', 0)
        sl = row.get('SL Level', 0)
        
        st.markdown(f"""
        <div class="context-row">
            <span><b>ENT:</b> {entry_p}</span>
            <span style="color: #15803d;"><b>TGT:</b> {tgt}</span>
            <span style="color: #b91c1c;"><b>SL:</b> {sl}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Links
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
            # Maintained 5 columns for minimal scrolling
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
