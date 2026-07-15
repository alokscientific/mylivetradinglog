import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# Page config
st.set_page_config(page_title="TRADE LOG SYSTEM", page_icon="📈", layout="wide")

# Architectural & Dual-Theme (Light/Dark) Adaptive CSS
st.markdown("""
<style>
/* Font Setup */
html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Header Alignment Fix */
.header-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 20px;
}
.main-title {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 800;
    font-size: 1.8rem;
    letter-spacing: 1.5px;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    margin-bottom: 8px;
}
.sub-title {
    color: var(--text-color);
    opacity: 0.7;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Card Design - Adaptive Blue Outline & Hover Effects */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    border-top: 4px solid #2563eb !important;
    border-radius: 10px !important;
    background-color: transparent !important; /* Adaptive background */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    padding: 1rem !important;
    transition: all 0.3s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59, 130, 246, 0.8) !important;
    box-shadow: 0 4px 25px rgba(37, 99, 235, 0.2) !important;
    transform: translateY(-2px);
}

/* Metric text color fix for dark mode */
div[data-testid="stMetricValue"] {
    font-size: 1.2rem !important; 
    font-weight: 700 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    opacity: 0.7;
    text-transform: uppercase;
}

/* Data Grid Layout (Semi-transparent for both themes) */
.data-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    background-color: rgba(148, 163, 184, 0.05);
    padding: 10px;
    border-radius: 6px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    margin: 12px 0;
}
.data-item {
    display: flex;
    flex-direction: column;
}
.data-label {
    color: var(--text-color);
    opacity: 0.6;
    font-weight: 600;
    font-size: 0.65rem;
    margin-bottom: 2px;
}
.data-value {
    font-weight: 700;
    color: var(--text-color);
    font-size: 0.85rem;
}

/* Universal Red/Green text that looks good on dark and light */
.text-green { color: #10b981 !important; }
.text-red { color: #ef4444 !important; }
.text-blue { color: #3b82f6 !important; }

/* News Section */
.news-section {
    background: linear-gradient(90deg, rgba(59,130,246,0.15) 0%, rgba(59,130,246,0.02) 100%);
    border-left: 3px solid #3b82f6;
    padding: 8px 10px;
    border-radius: 4px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
}
.news-icon {
    font-size: 1.1rem;
    margin-right: 10px;
}
.news-marquee {
    color: #60a5fa;
    font-weight: 600;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# Properly Aligned Header
st.markdown("""
<div class="header-container">
    <div class="main-title">TRADE LOG SYSTEM</div>
    <div class="sub-title">Track & Trade Terminal</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# Live News Fetching Function (Uses Google News RSS)
@st.cache_data(ttl=1800) # Caches news for 30 mins to avoid slowdowns
def get_live_news(company_name):
    try:
        clean_name = company_name.split()[0] # Take first word to improve search
        query = urllib.parse.quote(f"{clean_name} stock news India")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=3)
        root = ET.fromstring(response.read())
        
        # Get top 2 headlines
        headlines = [item.find('title').text for item in root.findall('.//item')[:2]]
        if headlines:
            return " &nbsp; ✦ &nbsp; ".join(headlines)
    except:
        pass
    return f"Scanning latest market movements and structural shifts for {company_name}..."

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

def draw_card(row):
    with st.container(border=True):
        raw_symbol = str(row['Stock Symbol']).strip()
        clean_symbol = raw_symbol.split(':')[-1] if ':' in raw_symbol else raw_symbol
        company_name = str(row.get('Company Name', '--'))
        
        status = str(row.get('Status', 'IN TRADE'))
        
        if status == "TARGET HIT":
            status_html = "<span style='color: #10b981; font-weight: 800; font-size: 0.8rem; background: rgba(16,185,129,0.1); padding: 3px 8px; border-radius: 4px;'>■ TARGET HIT</span>"
        elif status == "SL HIT":
            status_html = "<span style='color: #ef4444; font-weight: 800; font-size: 0.8rem; background: rgba(239,68,68,0.1); padding: 3px 8px; border-radius: 4px;'>■ SL HIT</span>"
        else:
            status_html = "<span style='color: #3b82f6; font-weight: 800; font-size: 0.8rem; background: rgba(59,130,246,0.1); padding: 3px 8px; border-radius: 4px;'>■ ACTIVE</span>"

        entry_date = str(row.get('Entry Date', '--')).split(' ')[0]
        if entry_date == 'nan': entry_date = '--'
        hit_date = str(row.get('Hit Date', '--')).split(' ')[0]
        if hit_date == 'nan': hit_date = '--'

        date_str = f"ENTRY: {entry_date}"
        if status in ["TARGET HIT", "SL HIT"] and hit_date != '--':
            date_str += f" &nbsp;|&nbsp; EXIT: {hit_date}"

        # Header Module
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
                <div style="font-weight: 800; font-size: 1.2rem; line-height: 1.2;">{clean_symbol}</div>
                <div style="font-size: 0.75rem; opacity: 0.7; max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{company_name}</div>
                <div style="font-size: 0.65rem; opacity: 0.5; font-weight: 600; margin-top: 3px;">{date_str}</div>
            </div>
            <div>{status_html}</div>
        </div>
        """, unsafe_allow_html=True)

        live_p = row.get('Live Price', 0)
        pnl_val = format_pct(row.get('Live P&L %', 0))
        
        # Change % Fix
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

        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="LIVE PRICE", value=f"₹{live_p}", delta=change_str)
        with c2:
            st.metric(label="LIVE P&L", value=pnl_val)

        entry_p = row.get('Entry Price', 0)
        tgt = row.get('Target Price', 0)
        sl = row.get('SL Level', 0)
        
        # Grid Data Module
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
        
        # Dynamic News Ticker
        latest_news = get_live_news(company_name)
        st.markdown(f"""
        <div class="news-section">
            <span class="news-icon">📰</span> 
            <marquee class="news-marquee" scrollamount="4" onmouseover="this.stop();" onmouseout="this.start();">
                <a href="https://www.google.com/search?q={company_name.replace(' ', '+')}+stock+news&tbm=nws" target="_blank" style="color: inherit; text-decoration: none;">
                    {latest_news}
                </a>
            </marquee>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons
        btn1, btn2 = st.columns(2)
        with btn1:
            st.link_button("DATA", f"https://www.screener.in/company/{clean_symbol}/", use_container_width=True)
        with btn2:
            st.link_button("CHART", f"https://in.tradingview.com/chart/?symbol={raw_symbol}", use_container_width=True)

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
