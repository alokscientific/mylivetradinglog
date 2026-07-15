import streamlit as st
import pandas as pd

# Page config - Structural Layout
st.set_page_config(page_title="TRADE LOG SYSTEM", page_icon="📈", layout="wide")

# Architectural & Institutional CSS
st.markdown("""
<style>
/* Main Background and Font Setup */
html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Structural Card Design - FULL BLUE OUTLINE */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1.5px solid #1e40af !important; /* Full Blue Outline */
    border-radius: 6px !important;
    background-color: #ffffff;
    box-shadow: 0 4px 6px rgba(30, 64, 175, 0.08) !important;
    padding: 0.75rem !important;
}

/* Metric Adjustments for Clean Hierarchy */
div[data-testid="stMetricValue"] {
    font-size: 1.15rem !important; 
    font-weight: 700 !important;
    color: #0f172a !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
}

/* Data Grid Layout */
.data-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 5px;
    background-color: #f8fafc;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    margin: 10px 0;
    font-size: 0.75rem;
}
.data-item {
    display: flex;
    flex-direction: column;
}
.data-label {
    color: #64748b;
    font-weight: 600;
    font-size: 0.65rem;
}
.data-value {
    font-weight: 700;
    color: #1e293b;
}

/* Functional Colors */
.text-green { color: #15803d !important; }
.text-red { color: #b91c1c !important; }
.text-blue { color: #1d4ed8 !important; }

/* News Section */
.news-section {
    font-size: 0.8rem;
    padding: 6px;
    background-color: #eff6ff;
    border-left: 3px solid #3b82f6;
    margin-bottom: 10px;
    border-radius: 0 4px 4px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.news-section a {
    color: #1e40af;
    text-decoration: none;
    font-weight: 700;
}
.news-section a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# Professional Header Module (Button Style)
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 10px 24px; border-radius: 6px; display: inline-block; font-weight: 800; font-size: 1.6rem; letter-spacing: 1px; margin-bottom: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    TRADE LOG SYSTEM
</div>
<div style="color: #475569; font-size: 0.95rem; font-weight: 600; margin-bottom: 25px; letter-spacing: 0.5px;">
    Track & Trade Terminal
</div>
""", unsafe_allow_html=True)

# Core Data Connection
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

# Architectural Card Component
def draw_card(row):
    with st.container(border=True):
        raw_symbol = str(row['Stock Symbol']).strip()
        clean_symbol = raw_symbol.split(':')[-1] if ':' in raw_symbol else raw_symbol
        company_name = str(row.get('Company Name', '--'))
        
        status = str(row.get('Status', 'IN TRADE'))
        
        # Color Logic for Status
        if status == "TARGET HIT":
            status_html = "<span style='color: #15803d; font-weight: 800; font-size: 0.8rem;'>■ TARGET HIT</span>"
        elif status == "SL HIT":
            status_html = "<span style='color: #b91c1c; font-weight: 800; font-size: 0.8rem;'>■ SL HIT</span>"
        else:
            status_html = "<span style='color: #1d4ed8; font-weight: 800; font-size: 0.8rem;'>■ ACTIVE</span>"

        # Date Management
        entry_date = str(row.get('Entry Date', '--')).split(' ')[0]
        if entry_date == 'nan': entry_date = '--'
        
        hit_date = str(row.get('Hit Date', '--')).split(' ')[0]
        if hit_date == 'nan': hit_date = '--'

        date_str = f"ENTRY: {entry_date}"
        if status in ["TARGET HIT", "SL HIT"] and hit_date != '--':
            date_str += f" &nbsp;|&nbsp; EXIT: {hit_date}"

        # 1. Header (Symbol, Status & Dates)
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
            <div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #0f172a; line-height: 1.2;">{clean_symbol}</div>
                <div style="font-size: 0.7rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px;">{company_name}</div>
                <div style="font-size: 0.65rem; color: #94a3b8; font-weight: 600; margin-top: 3px;">{date_str}</div>
            </div>
            <div>{status_html}</div>
        </div>
        """, unsafe_allow_html=True)

        # Variables for Main Data
        live_p = row.get('Live Price', 0)
        pnl_val = format_pct(row.get('Live P&L %', 0))
        
        # Robust Today's Change % Fix
        t_change_raw = str(row.get("Today's Change", "0")).strip()
        try:
            if '%' in t_change_raw:
                val = float(t_change_raw.replace('%', '').replace(',', ''))
                change_str = f"{val:+.2f}%"
            else:
                val = float(t_change_raw.replace(',', ''))
                if abs(val) < 1.0 and val != 0: 
                    change_str = f"{val * 100:+.2f}%"
                else:
                    change_str = f"{val:+.2f}%"
        except:
            change_str = "0.00%"

        # 2. Main Metrics (Live Data)
        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="LIVE PRICE", value=f"₹{live_p}", delta=change_str)
        with c2:
            st.metric(label="LIVE P&L", value=pnl_val)

        # 3. Detailed Data Grid
        entry_p = row.get('Entry Price', 0)
        tgt = row.get('Target Price', 0)
        sl = row.get('SL Level', 0)
        
        st.markdown(f"""
        <div class="data-grid">
            <div class="data-item">
                <span class="data-label">ENTRY POINT</span>
                <span class="data-value">₹{entry_p}</span>
            </div>
            <div class="data-item">
                <span class="data-label">TARGET</span>
                <span class="data-value text-green">₹{tgt}</span>
            </div>
            <div class="data-item">
                <span class="data-label">STOP LOSS</span>
                <span class="data-value text-red">₹{sl}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 4. Latest News Module
        news_query = company_name.replace(' ', '+')
        st.markdown(f"""
        <div class="news-section">
            <span style="font-size: 1.1rem;">📰</span> 
            <a href="https://www.google.com/search?q={news_query}+stock+news&tbm=nws" target="_blank">
                Latest News
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. External Actions
        btn1, btn2 = st.columns(2)
        with btn1:
            st.link_button("DATA", f"https://www.screener.in/company/{clean_symbol}/", use_container_width=True)
        with btn2:
            st.link_button("CHART", f"https://in.tradingview.com/chart/?symbol={raw_symbol}", use_container_width=True)

# Main Execution Render
if not df.empty:
    tab1, tab2 = st.tabs(["📊 ACTIVE TRADE", "📜 TRADE HISTORY"])

    with tab1:
        active_df = df[df['Status'].isin(["IN TRADE", "WAITING"])]
        if active_df.empty:
            st.info("System currently idle. No active tracking.")
        else:
            cols = st.columns(4)
            for index, row in active_df.iterrows():
                with cols[index % 4]:
                    draw_card(row)

    with tab2:
        history_df = df[df['Status'].isin(["SL HIT", "TARGET HIT"])]
        if history_df.empty:
            st.info("No closed logs found in the database.")
        else:
            cols = st.columns(4)
            history_df = history_df.reset_index(drop=True)
            for index, row in history_df.iterrows():
                with cols[index % 4]:
                    draw_card(row)
else:
    st.warning("⚠️ Critical: Data feed interrupted or source is empty.")
