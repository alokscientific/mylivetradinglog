import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import yfinance as yf

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
    margin-bottom: 25px;
}
.main-title {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 900;
    font-size: 1.8rem;
    letter-spacing: 1.5px;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    margin-bottom: 6px;
    display: inline-block;
}
.sub-title {
    color: var(--text-color);
    opacity: 0.7;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-left: 24px;
}

/* Card Design - Adaptive Blue Outline & Hover Effects */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    border-top: 4px solid #2563eb !important;
    border-radius: 10px !important;
    background-color: transparent !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    padding: 1rem !important;
    transition: all 0.3s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59, 130, 246, 0.8) !important;
    box-shadow: 0 4px 25px rgba(37, 99, 235, 0.2) !important;
    transform: translateY(-2px);
}

/* Metric text adjustments */
div[data-testid="stMetricValue"] {
    font-size: 1.25rem !important; 
    font-weight: 800 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    opacity: 0.7;
    text-transform: uppercase;
}

/* Data Grid Layout */
.data-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    background-color: rgba(148, 163, 184, 0.05);
    padding: 12px;
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

/* Dynamic Live P&L Container Styling */
.pnl-container {
    display: flex;
    flex-direction: column;
}
.pnl-value {
    font-size: 1.25rem;
    font-weight: 800;
    margin-top: 4px;
}

/* Colors for specific values */
.text-green { color: #10b981 !important; }
.text-red { color: #ef4444 !important; }

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

# Properly Aligned Header Module
st.markdown("""
<div class="header-container">
    <div class="main-title">TRADE LOG SYSTEM</div>
    <div class="sub-title">Track & Trade Terminal</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# Live Real-Time Change from Yahoo Finance
@st.cache_data(ttl=60)
def get_yahoo_change(symbol):
    try:
        yf_sym = symbol.replace("NSE:", "").replace("BSE:", "") + ".NS"
        if "BSE:" in symbol: 
            yf_sym = symbol.replace("BSE:", "") + ".BO"
            
        tkr = yf.Ticker(yf_sym)
        prev = tkr.fast_info['previous_close']
        curr = tkr.fast_info['last_price']
        
        if prev and prev > 0:
            pct = ((curr - prev) / prev) * 100
            return f"{pct:+.2f}%"
    except:
        pass
    return None

# Live News Fetching Function
@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        clean_name = company_name.split()[0]
        query = urllib.parse.quote(f"{clean_name} stock news India")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=3)
        root = ET.fromstring(response.read())
        
        headlines = [item.find('title').text for item in root.findall('.//item')[:2]]
        if headlines:
            return " &nbsp; ✦ &nbsp; ".join(headlines)
    except:
        pass
    return f"Tracking latest technical updates and alerts for {company_name}..."

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

# Process Live P&L Function with dynamic sign and styling
def get_pnl_html(val_raw):
    try:
        if pd.isna(val_raw): 
            return '<span class="pnl-value">0.00%</span>'
        
        val_str = str(val_raw).replace('%', '').replace(',', '').strip()
        val = float(val_str)
        
        # Check if sheet contains raw decimals
        if abs(val) < 1.0 and val != 0:
            val = val * 100
            
        if val > 0:
            return f'<span class="pnl-value text-green">+{val:.2f}%</span>'
        elif val < 0:
            return f'<span class="pnl-value text-red">{val:.2f}%</span>'
        else:
            return f'<span class="pnl-value">0.00%</span>'
    except:
        return '<span class="pnl-value">0.00%</span>'

def draw_card(row):
    with st.container(border=True):
        raw_symbol = str(row['Stock Symbol']).strip()
        clean_symbol = raw_symbol.split(':')[-1] if ':' in raw_symbol else raw_symbol
        company_name = str(row.get('Company Name', '--'))
        
        status = str(row.get('Status', 'IN TRADE')).strip().upper()
        
        # BADGE LOGIC
        if status == "TARGET HIT":
            status_html = "<span style='color: #10b981; font-weight: 800; font-size: 0.8rem; background: rgba(16,185,129,0.1); padding: 3px 8px; border-radius: 4px;'>■ TARGET HIT</span>"
        elif status == "SL HIT":
            status_html = "<span style='color: #ef4444; font-weight: 800; font-size: 0.8rem; background: rgba(239,68,68,0.1); padding: 3px 8px; border-radius: 4px;'>■ SL HIT</span>"
        elif status == "WAITING":
            status_html = "<span style='color: #f59e0b; font-weight: 800; font-size: 0.8rem; background: rgba(245,158,11,0.1); padding: 3px 8px; border-radius: 4px;'>⏳ PENDING</span>"
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
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
            <div>
                <div style="font-weight: 900; font-size: 1.3rem; line-height: 1.1;">{clean_symbol}</div>
                <div style="font-size: 0.75rem; opacity: 0.7; max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px;">{company_name}</div>
                <div style="font-size: 0.65rem; opacity: 0.5; font-weight: 600; margin-top: 4px;">{date_str}</div>
            </div>
            <div>{status_html}</div>
        </div>
        """, unsafe_allow_html=True)

        live_p = row.get('Live Price', 0)
        
        # Real-time Yahoo Finance Delta Integration
        yf_change = get_yahoo_change(raw_symbol)
        if yf_change:
            change_str = yf_change
        else:
            t_change_raw = str(row.get("Today's Change", "0")).strip()
            try:
                if '%' in t_change_raw:
                    val = float(t_change_raw.replace('%', '').replace(',', ''))
                    change_str = f"{val:+.2f}%"
                else:
                    val = float(t_change_raw.replace(',', ''))
                    change_str = f"{val * 100:+.2f}%" if abs(val) < 1.0 and val != 0 else f"{val:+.2f}%"
            except:
                change_str = "0.00%"

        # Main Layout: Live Price & Custom Styled Live P&L
        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="LIVE PRICE", value=f"₹{live_p}", delta=change_str)
        with c2:
            # P&L Logic Fix for WAITING Status
            if status == "WAITING":
                pnl_html = '<span class="pnl-value" style="opacity: 0.5;">--</span>'
            else:
                pnl_html = get_pnl_html(row.get('Live P&L %', 0))
                
            st.markdown(f"""
            <div class="pnl-container">
                <div class="st-emotion-cache-1qmj432" style="font-size: 0.75rem; font-weight: 600; opacity: 0.7; text-transform: uppercase;">LIVE P&L</div>
                {pnl_html}
            </div>
            """, unsafe_allow_html=True)

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
