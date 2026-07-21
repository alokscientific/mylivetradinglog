import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import yfinance as yf
import time

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

@st.cache_data(ttl=5)
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

# 🔥 DIRECT HTML P&L GENERATOR 🔥
def get_pnl_html(val):
    try:
        if pd.isna(val) or val == "" or val == "--":
            return '<span class="pnl-value">0.00%</span>'
            
        if isinstance(val, str):
            if '%' in val:
                val = float(val.replace('%', '').replace(',', ''))
            else:
                val = float(val.replace(',', ''))
                
        if val > 0:
            return f'<span class="pnl-value text-green">+{val:.2f}%</span>'
        elif val < 0:
            return f'<span class="pnl-value text-red">{val:.2f}%</span>'
        else:
            return f'<span class="pnl-value">0.00%</span>'
    except:
        return '<span class="pnl-value">0.00%</span>'

# 🔥 NEW COMPACT CARD DESIGN WITH EXPANDER 🔥
def draw_card(row):
    with st.container(border=True):
        raw_symbol = str(row['Stock Symbol']).strip()
        clean_symbol = raw_symbol.split(':')[-1] if ':' in raw_symbol else raw_symbol
        company_name = str(row.get('Company Name', '--'))
        
        status = str(row.get('Status', 'IN TRADE')).strip().upper()
        
        # BADGE LOGIC
        if status == "TARGET HIT":
            status_html = "<span style='color: #10b981; font-weight: 800; font-size: 0.7rem; background: rgba(16,185,129,0.1); padding: 3px 8px; border-radius: 4px;'>■ TARGET HIT</span>"
        elif status == "SL HIT":
            status_html = "<span style='color: #ef4444; font-weight: 800; font-size: 0.7rem; background: rgba(239,68,68,0.1); padding: 3px 8px; border-radius: 4px;'>■ SL HIT</span>"
        elif status == "WAITING":
            status_html = "<span style='color: #f59e0b; font-weight: 800; font-size: 0.7rem; background: rgba(245,158,11,0.1); padding: 3px 8px; border-radius: 4px;'>⏳ PENDING</span>"
        else:
            status_html = "<span style='color: #3b82f6; font-weight: 800; font-size: 0.7rem; background: rgba(59,130,246,0.1); padding: 3px 8px; border-radius: 4px;'>■ ACTIVE</span>"

        entry_date = str(row.get('Entry Date', '--')).split(' ')[0]
        if entry_date == 'nan': entry_date = '--'
        hit_date = str(row.get('Hit Date', '--')).split(' ')[0]
        if hit_date == 'nan': hit_date = '--'

        date_str = f"ENTRY: {entry_date}"
        if status in ["TARGET HIT", "SL HIT"] and hit_date != '--':
            date_str += f" &nbsp;|&nbsp; EXIT: {hit_date}"

        live_p_raw = row.get('Live Price', 0)
        entry_p_raw = row.get('Entry Price', 0)
        
        # --- TODAY'S CHANGE LOGIC ---
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

        change_color = "#10b981" if "+" in change_str else "#ef4444" if "-" in change_str else "inherit"

        # --- LIVE P&L LOGIC ---
        if status == "WAITING":
            pnl_html = '<span style="font-weight: 800; opacity: 0.5;">--</span>'
        else:
            calculated_pnl = 0.0
            if status == "IN TRADE":
                try:
                    e_val = float(str(entry_p_raw).replace(',', ''))
                    l_val = float(str(live_p_raw).replace(',', ''))
                    if e_val > 0 and l_val > 0:
                        calculated_pnl = ((l_val - e_val) / e_val) * 100
                except:
                    pass
            else:
                calculated_pnl = row.get('Live P&L %', 0)

            if calculated_pnl > 0:
                pnl_html = f'<span style="color: #10b981; font-weight: 800;">+{calculated_pnl:.2f}%</span>'
            elif calculated_pnl < 0:
                pnl_html = f'<span style="color: #ef4444; font-weight: 800;">{calculated_pnl:.2f}%</span>'
            else:
                pnl_html = f'<span style="font-weight: 800;">0.00%</span>'

        # ==========================================
        # 1. VISIBLE COMPACT HEADER (Yeh hamesha dikhega)
        # ==========================================
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="font-weight: 900; font-size: 1.3rem; line-height: 1.1;">{clean_symbol}</div>
            <div>{status_html}</div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(148, 163, 184, 0.05); padding: 10px; border-radius: 6px; margin-bottom: 5px; border: 1px solid rgba(148, 163, 184, 0.1);">
            <div>
                <div style="font-size: 0.65rem; opacity: 0.7; font-weight: 700;">TODAY'S CHG</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: {change_color};">{change_str}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.65rem; opacity: 0.7; font-weight: 700;">LIVE P&L</div>
                <div style="font-size: 1.05rem;">{pnl_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ==========================================
        # 2. EXPANDABLE DETAILS (Dropdown ke andar wala hissa)
        # ==========================================
        with st.expander("View Trade Details"):
            st.markdown(f"""
            <div style="font-size: 0.85rem; opacity: 0.9; font-weight: 600; margin-bottom: 2px;">{company_name}</div>
            <div style="font-size: 0.7rem; opacity: 0.6; font-weight: 600; margin-bottom: 15px;">{date_str}</div>
            """, unsafe_allow_html=True)
            
            st.metric(label="LIVE PRICE", value=f"₹{live_p_raw}")

            tgt = row.get('Target Price', 0)
            sl = row.get('SL Level', 0)
            
            st.markdown(f"""
            <div class="data-grid">
                <div class="data-item">
                    <span class="data-label">ENTRY POINT</span>
                    <span class="data-value">₹{entry_p_raw}</span>
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
            
            btn1, btn2 = st.columns(2)
            with btn1:
                st.link_button("DATA", f"https://www.screener.in/company/{clean_symbol}/", use_container_width=True)
            with btn2:
                st.link_button("CHART", f"https://in.tradingview.com/chart/?symbol={raw_symbol}", use_container_width=True)

if not df.empty:
    
    # ==========================================
    # 🚀 PORTFOLIO SUMMARY DASHBOARD (SAFE MODE)
    # ==========================================
    active_trades_df = df[df['Status'].isin(["IN TRADE"])]
    closed_trades_df = df[df['Status'].isin(["SL HIT", "TARGET HIT"])]
    
    total_active = len(active_trades_df)
    total_closed = len(closed_trades_df)

    def extract_raw_val(val_raw):
        try:
            if pd.isna(val_raw): return 0.0
            val_str = str(val_raw).strip()
            if '%' in val_str:
                return float(val_str.replace('%', '').replace(',', ''))
            else:
                val = float(val_str.replace(',', ''))
                if abs(val) < 1.0 and val != 0:
                    return val * 100
                return val
        except:
            return 0.0

    # 🔥 SAFE ON-THE-FLY CUMULATIVE P&L CALCULATION
    cumulative_pnl = 0.0
    for _, row in active_trades_df.iterrows():
        try:
            e_val = float(str(row.get('Entry Price', 0)).replace(',', ''))
            l_val = float(str(row.get('Live Price', 0)).replace(',', ''))
            if e_val > 0 and l_val > 0:
                trade_pnl_pct = ((l_val - e_val) / e_val) * 100
                cumulative_pnl += trade_pnl_pct
        except:
            pass

    if "Today's Change" in active_trades_df.columns:
        today_change_pnl = sum(active_trades_df["Today's Change"].apply(extract_raw_val))
    else:
        today_change_pnl = 0.0

    # Determine Colors and Signs
    pnl_color = "#10b981" if cumulative_pnl > 0 else "#ef4444" if cumulative_pnl < 0 else "inherit"
    pnl_sign = "+" if cumulative_pnl > 0 else ""
    
    tc_color = "#10b981" if today_change_pnl > 0 else "#ef4444" if today_change_pnl < 0 else "inherit"
    tc_sign = "+" if today_change_pnl > 0 else ""

    st.markdown("##### 🚀 Portfolio Snapshot")
    
    # Custom HTML Summary Cards
    st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 25px;">
        <div style="flex: 1; padding: 15px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.2); background: rgba(59, 130, 246, 0.05); text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; opacity: 0.7; text-transform: uppercase;">Active Trades</div>
            <div style="font-size: 1.8rem; font-weight: 900;">{total_active}</div>
        </div>
        <div style="flex: 1; padding: 15px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.2); background: rgba(59, 130, 246, 0.05); text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; opacity: 0.7; text-transform: uppercase;">Closed Trades</div>
            <div style="font-size: 1.8rem; font-weight: 900;">{total_closed}</div>
        </div>
        <div style="flex: 2; padding: 15px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.2); background: rgba(59, 130, 246, 0.05); text-align: center; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 0.75rem; font-weight: 700; opacity: 0.7; text-transform: uppercase; margin-bottom: 5px;">Cumulative P&L (Active)</div>
            <div style="display: flex; justify-content: center; align-items: baseline; gap: 12px;">
                <div style="font-size: 2rem; font-weight: 900; color: {pnl_color}; line-height: 1;">{pnl_sign}{cumulative_pnl:.2f}%</div>
                <div style="font-size: 0.9rem; font-weight: 700; color: {tc_color}; background: {tc_color}1A; padding: 3px 8px; border-radius: 4px;">{tc_sign}{today_change_pnl:.2f}% Today</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ==========================================

    tab1, tab2 = st.tabs(["📊 ACTIVE TRADE", "📜 TRADE HISTORY"])

    with tab1:
        active_df = df[df['Status'].isin(["IN TRADE"])]
        if active_df.empty:
            st.info("System currently idle. No active tracking.")
        else:
            cols = st.columns(4)
            active_df = active_df.reset_index(drop=True)
            for index, row in active_df.iterrows():
                with cols[index % 4]:
                    draw_card(row)

    # ==========================================
    # TRADE HISTORY TAB KELIYE COMPLETE CODE
    # ==========================================
    with tab2:
        st.header("📜 Trade History")
        
        # Closed trades ka data copy kar rahe hain
        history_df = closed_trades_df.copy()
        
        if not history_df.empty:
            # --- 1. DATA CLEANING & CALCULATION ---
            
            # Dates ko proper format me convert karna
            history_df['Entry Date'] = pd.to_datetime(history_df['Entry Date'], format='%d/%m/%Y', errors='coerce')
            history_df['Hit Date'] = pd.to_datetime(history_df['Hit Date'], format='%d/%m/%Y', errors='coerce')

            # Days Held nikalna (Hit Date - Entry Date)
            history_df['Days Held'] = (history_df['Hit Date'] - history_df['Entry Date']).dt.days
            history_df['Days Held'] = history_df['Days Held'].fillna(0).astype(int)

            # Numbers ko clean karke float (decimal) me badalna
            def clean_number(val):
                if pd.isna(val) or val == 'None' or val == '':
                    return 0.0
                return float(str(val).replace('%', '').replace('+', '').replace(',', '').strip())

            # 🔥 NAYA SMART LOGIC: STATUS KE HISAB SE ACTUAL P&L 🔥
            def calculate_closed_pnl(row):
                status = str(row.get('Status', '')).strip().upper()
                if status == 'TARGET HIT':
                    return clean_number(row.get('Target %', 0))
                elif status == 'SL HIT':
                    # Stop loss hai toh return ko automatically negative bana dega
                    return -abs(clean_number(row.get('SL %', 0)))
                else:
                    return 0.0

            # Actual locked P&L column generate karna
            history_df['Trade P&L (%) Num'] = history_df.apply(calculate_closed_pnl, axis=1)
            history_df['Entry Price Num'] = history_df['Entry Price'].apply(clean_number)

            # Totals nikalna (Closed trades ka exact locked total)
            total_cumulative_pnl = history_df['Trade P&L (%) Num'].sum()
            total_cumulative_days = history_df['Days Held'].sum()

            # --- 2. TOP METRICS DIKHANA ---
            st.markdown("### 📊 Overall Performance")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Cumulative P&L", value=f"{total_cumulative_pnl:+.2f}%")
            with col2:
                st.metric(label="Cumulative Days in Trades", value=f"{total_cumulative_days} Days")
            
            st.divider()

            # --- 3. FILTER & RENAME COLUMNS ---
            # Dashboard ke display ke liye clean column setup karna
            history_df['Trade P&L (%)'] = history_df['Trade P&L (%) Num']
            
            columns_to_keep = ['Stock Symbol', 'Company Name', 'Entry Date', 'Hit Date', 'Days Held', 'Entry Price Num', 'Trade P&L (%)', 'Status']
            
            columns_to_keep = [col for col in columns_to_keep if col in history_df.columns]
            display_df = history_df[columns_to_keep].copy()

            # Columns ko clean naam dena
            display_df = display_df.rename(columns={
                'Entry Price Num': 'Entry Price'
            })

            # --- 4. COLOR CODING FUNCTIONS ---
            def color_status(val):
                val_str = str(val).strip().upper()
                if val_str == 'TARGET HIT':
                    return 'color: #00FF00; font-weight: bold;' 
                elif val_str == 'SL HIT':
                    return 'color: #FF0000; font-weight: bold;' 
                return ''

            def color_pnl(val):
                val_str = str(val)
                if '+' in val_str or (isinstance(val, (int, float)) and val > 0):
                    return 'color: #00FF00;' 
                elif '-' in val_str or (isinstance(val, (int, float)) and val < 0):
                    return 'color: #FF0000;' 
                return ''

            # --- 5. TABLE STYLING & 2-DECIMAL FORMATTING ---
            
            format_dict = {
                "Entry Date": lambda t: t.strftime('%d/%m/%Y') if not pd.isna(t) else "--",
                "Hit Date": lambda t: t.strftime('%d/%m/%Y') if not pd.isna(t) else "--",
                "Entry Price": "{:.2f}",  
                "Trade P&L (%)": lambda x: f"{clean_number(x):+.2f}%" 
            }

            styled_history_df = display_df.style.map(color_status, subset=['Status']) \
                                                .map(color_pnl, subset=['Trade P&L (%)']) \
                                                .format(format_dict)

            # Final Table dikhana
            st.dataframe(styled_history_df, use_container_width=True, hide_index=True)

        else:
            st.info("No closed trades found in history yet.")
            
time.sleep(5)
st.rerun()
