import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
import plotly.io as pio

# --- Streamlit Dashboard Config ---
st.set_page_config(
    page_title="Quantum Stock Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Color Theme ---
BACKGROUND_COLOR = "#0f1721"
CARD_BGCOLOR = "#1a2332"
ACCENT_COLOR = "#38b2ac"
TEXT_COLOR = "#e2e8f0"
MUTED_COLOR = "#a0aec0"
CHART_GRIDCOLOR = "#2d3748"
BUY_COLOR = "#38b2ac"  # Teal
SELL_COLOR = "#e53e3e"  # Red
FORECAST_COLOR = "#6b46c1"  # Purple
PRICE_COLOR = "#f6e05e"  # Yellow
MA_SHORT_COLOR = "#4299e1"  # Blue
MA_LONG_COLOR = "#ed64a6"  # Pink

# --- Custom CSS ---
st.markdown("""
    <style>
    /* Global Styles */
    html, body, [class*="css"] {
        background-color: """ + BACKGROUND_COLOR + """;
        color: """ + TEXT_COLOR + """;
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: """ + BACKGROUND_COLOR + """;
    }
    
    /* Main Container */
    .block-container {
        padding: 3rem 1rem 2rem 1rem;
        max-width: 1200px;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: """ + CARD_BGCOLOR + """;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 1rem;
    }
    
    /* Headers */
    h1 {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: white !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
        border-left: 4px solid """ + ACCENT_COLOR + """;
        padding-left: 12px;
    }
    
    h2, h3 {
        font-weight: 600 !important;
        color: white !important;
        letter-spacing: -0.3px;
    }
    
    h4 {
        font-size: 18px !important;
        font-weight: 500 !important;
        color: """ + MUTED_COLOR + """ !important;
        margin-bottom: 1rem !important;
    }
    
    /* Stat Cards */
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background-color: """ + CARD_BGCOLOR + """;
        padding: 1.25rem;
        border-radius: 8px;
        flex: 1;
        min-width: 160px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.12);
    }
    
    .metric-label {
        font-size: 14px;
        color: """ + MUTED_COLOR + """;
        font-weight: 400;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: white;
        letter-spacing: -0.5px;
    }
    
    /* Analysis Box */
    .analysis-container {
        background-color: """ + CARD_BGCOLOR + """;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .signal-box {
        padding: 12px 16px;
        border-radius: 6px;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
    }
    
    .buy-signal {
        background-color: rgba(56, 178, 172, 0.15);
        color: """ + BUY_COLOR + """;
        border: 1px solid rgba(56, 178, 172, 0.3);
    }
    
    .sell-signal {
        background-color: rgba(229, 62, 62, 0.15);
        color: """ + SELL_COLOR + """;
        border: 1px solid rgba(229, 62, 62, 0.3);
    }
    
    /* Sidebar Style */
    .sidebar-title {
        font-size: 16px;
        font-weight: 600;
        color: white;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .logo-container {
        padding: 0.5rem 0 1.5rem 0;
        text-align: center;
    }
    
    .st-bw {
        color: """ + TEXT_COLOR + """ !important;
    }
    
    /* Disclaimer */
    .disclaimer-box {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 8px;
        font-size: 14px;
        color: """ + MUTED_COLOR + """;
        margin-top: 2rem;
        line-height: 1.5;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Section Dividers */
    hr {
        margin: 1.5rem 0;
        border-color: rgba(255, 255, 255, 0.05);
    }
    
    /* Footer */
    .footer-text {
        margin: 2rem auto 1rem;
        text-align: center;
        font-size: 14px;
        color: """ + MUTED_COLOR + """;
    }
    
    /* Table Styling */
    .dataframe {
        font-size: 14px !important;
    }
    
    th {
        background-color: """ + CARD_BGCOLOR + """ !important;
        color: white !important;
    }
    
    td {
        background-color: """ + BACKGROUND_COLOR + """ !important;
        color: """ + TEXT_COLOR + """ !important;
    }
    
    /* Custom Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: nowrap;
        font-size: 14px;
        font-weight: 500;
        color: """ + MUTED_COLOR + """;
        border-radius: 4px 4px 0 0;
        background-color: """ + CARD_BGCOLOR + """;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: """ + CARD_BGCOLOR + """;
        color: white !important;
        border-bottom: 2px solid """ + ACCENT_COLOR + """ !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- Custom Function for Metric Cards ---
def metric_card(label, value, prefix="", suffix=""):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
    </div>
    """

# --- Custom Function for Signal Box ---
def signal_box(signal_type, message):
    signal_class = "buy-signal" if signal_type == "BUY" else "sell-signal"
    icon = "🚀" if signal_type == "BUY" else "🔻"
    return f"""
    <div class="signal-box {signal_class}">
        {icon} {message}
    </div>
    """

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="logo-container"><h2>Quantum Analysis</h2></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-title">📈 Stock Parameters</div>', unsafe_allow_html=True)
    ticker = st.text_input("Stock Ticker (Yahoo Finance)", value="BBCA.JK")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
    with col2:
        end_date = st.date_input("End Date", value=datetime.today())
    
    st.markdown('<div class="sidebar-title">📊 Technical Indicators</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        short_window = st.number_input("Short MA", min_value=5, max_value=100, value=50)
    with col2:
        long_window = st.number_input("Long MA", min_value=20, max_value=500, value=200)
    
    st.markdown('<div class="sidebar-title">🔮 Forecast Settings</div>', unsafe_allow_html=True)
    forecast_days = st.slider("Forecast Days", min_value=7, max_value=60, value=30)
    
    st.markdown('<div class="sidebar-title">💰 Backtesting</div>', unsafe_allow_html=True)
    initial_capital = st.number_input("Initial Capital", min_value=1000000, max_value=1000000000, value=10000000, step=1000000, format="%d")

# --- Header ---
st.markdown(f"<h1>Quantum Stock Analysis</h1>", unsafe_allow_html=True)
st.markdown(f"<h4>Advanced Technical Analysis & Forecasting Engine</h4>", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data(ttl=3600)
def load_stock_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date)

with st.spinner('Loading market data...'):
    data = load_stock_data(ticker, start_date, end_date)
    
if data.empty:
    st.error("❌ No data found. Please check the stock ticker and date range.")
    st.stop()

# --- Preprocessing ---
#df = data.reset_index()[['Date', 'Close']].dropna()
data = data.reset_index()

# Handle MultiIndex columns from yfinance
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]

df = data[['Date', 'Close']].dropna()

df.columns = ['ds', 'y']
df['ds'] = pd.to_datetime(df['ds'])
df['y'] = pd.to_numeric(df['y'], errors='coerce')
df.dropna(inplace=True)

# --- Calculate Moving Averages ---
df['MA_Short'] = df['y'].rolling(window=short_window).mean()
df['MA_Long'] = df['y'].rolling(window=long_window).mean()
df['Signal'] = 0
df.loc[df['MA_Short'] > df['MA_Long'], 'Signal'] = 1
df['Position'] = df['Signal'].diff()

# --- Get Additional Stats ---
latest = df.iloc[-1]
current_price = latest['y']
prev_close = df.iloc[-2]['y'] if len(df) > 1 else current_price
price_change = current_price - prev_close
price_change_pct = (price_change / prev_close) * 100 if prev_close > 0 else 0
ma_diff_pct = ((latest['MA_Short'] - latest['MA_Long']) / latest['MA_Long']) * 100 if latest['MA_Long'] > 0 else 0
avg_price = df['y'].mean()
min_price = df['y'].min()
max_price = df['y'].max()

# --- ARIMA Forecasting (Tuned for better fluctuation) ---
try:
    model = ARIMA(df['y'], order=(8, 1, 5))
    model_fit = model.fit()
    forecast_values = model_fit.forecast(steps=forecast_days)
    forecast_index = pd.date_range(start=df['ds'].iloc[-1], periods=forecast_days+1, freq='B')[1:]
    forecast_df = pd.DataFrame({'ds': forecast_index, 'yhat': forecast_values})
    forecast_error = False
except Exception as e:
    st.warning(f"⚠️ Forecasting encountered an issue. Using simpler model.")
    try:
        # Fallback to simpler model
        model = ARIMA(df['y'], order=(1, 1, 0))
        model_fit = model.fit()
        forecast_values = model_fit.forecast(steps=forecast_days)
        forecast_index = pd.date_range(start=df['ds'].iloc[-1], periods=forecast_days+1, freq='B')[1:]
        forecast_df = pd.DataFrame({'ds': forecast_index, 'yhat': forecast_values})
        forecast_error = False
    except:
        forecast_error = True
        st.error("Unable to generate forecast with the current data.")

# --- Metrics Cards ---
st.markdown('<div class="metric-container">', unsafe_allow_html=True)
st.markdown(metric_card("Current Price", f"{current_price:,.2f}", suffix=f" ({price_change_pct:+.2f}%)"), unsafe_allow_html=True)
st.markdown(metric_card(f"MA{short_window}", f"{latest['MA_Short']:,.2f}"), unsafe_allow_html=True)
st.markdown(metric_card(f"MA{long_window}", f"{latest['MA_Long']:,.2f}"), unsafe_allow_html=True)
st.markdown(metric_card("MA Difference", f"{ma_diff_pct:+.2f}", suffix="%"), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Signal Box ---
signal = "BUY" if latest['Signal'] == 1 else "SELL / HOLD"
signal_message = f"Signal: {signal} (Short MA {'>' if latest['MA_Short'] > latest['MA_Long'] else '<='} Long MA)"
st.markdown(signal_box(signal if signal == "BUY" else "SELL", signal_message), unsafe_allow_html=True)

# --- Main Content Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Chart Analysis", "📊 Backtesting Results", "📘 Technical Explanation"])

with tab1:
    # --- Buy & Sell Signals ---
    buy_signals = df[df['Position'] == 1].copy()
    sell_signals = df[df['Position'] == -1].copy()
    
    # --- Plotly Chart ---
    fig = go.Figure()
    
    # Add traces in specific order (background to foreground)
    if not forecast_error:
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'], 
            y=forecast_df['yhat'], 
            mode='lines', 
            name='Forecast',
            line=dict(color=FORECAST_COLOR, width=2, dash='dot'),
            opacity=0.8
        ))
    
    # Add MA traces
    fig.add_trace(go.Scatter(
        x=df['ds'], 
        y=df['MA_Long'], 
        mode='lines', 
        name=f'MA{long_window}',
        line=dict(color=MA_LONG_COLOR, width=1.5),
        opacity=0.7
    ))
    
    fig.add_trace(go.Scatter(
        x=df['ds'], 
        y=df['MA_Short'], 
        mode='lines', 
        name=f'MA{short_window}',
        line=dict(color=MA_SHORT_COLOR, width=2),
        opacity=0.8
    ))
    
    # Main price line
    fig.add_trace(go.Scatter(
        x=df['ds'], 
        y=df['y'], 
        mode='lines', 
        name='Price',
        line=dict(color=PRICE_COLOR, width=2.5),
        opacity=0.9
    ))
    
    # Buy and sell signals
    fig.add_trace(go.Scatter(
        x=buy_signals['ds'], 
        y=buy_signals['y'], 
        mode='markers', 
        name='Buy Signal',
        marker=dict(
            symbol='triangle-up', 
            size=12, 
            color=BUY_COLOR, 
            line=dict(color='white', width=1)
        )
    ))
    
    fig.add_trace(go.Scatter(
        x=sell_signals['ds'], 
        y=sell_signals['y'], 
        mode='markers', 
        name='Sell Signal',
        marker=dict(
            symbol='triangle-down', 
            size=12, 
            color=SELL_COLOR, 
            line=dict(color='white', width=1)
        )
    ))
    
    # Current price point
    fig.add_trace(go.Scatter(
        x=[latest['ds']], 
        y=[latest['y']], 
        mode='markers', 
        name='Latest',
        marker=dict(
            symbol='circle', 
            size=10, 
            color='white', 
            line=dict(color=ACCENT_COLOR, width=2)
        ),
        hoverinfo='y'
    ))
    
    # Update layout with professional styling
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR, family="Inter, Segoe UI, sans-serif"),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=12)
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridcolor=CHART_GRIDCOLOR,
            gridwidth=0.5,
            linecolor=CHART_GRIDCOLOR,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=CHART_GRIDCOLOR,
            gridwidth=0.5,
            zeroline=False,
            tickfont=dict(size=10),
            tickformat=',.0f'
        ),
        height=550
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})
    
    # Price Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Price", f"{avg_price:,.2f}")
    with col2:
        st.metric("Minimum Price", f"{min_price:,.2f}")
    with col3:
        st.metric("Maximum Price", f"{max_price:,.2f}")

with tab2:    
    # --- Backtesting ---
    position = 0.0
    cash = initial_capital
    buy_price = 0.0
    trade_log = []
    portfolio_history = []
    
    for i in range(1, len(df)):
        current_date = df['ds'].iloc[i]
        current_price = df['y'].iloc[i]
        current_value = cash + position * current_price
        
        portfolio_history.append({
            'Date': current_date,
            'Portfolio Value': current_value
        })
        
        if df['Position'].iloc[i] == 1 and position == 0:
            buy_price = current_price
            position = cash / buy_price
            cash = 0
            trade_log.append({
                'Date': current_date, 
                'Action': 'Buy', 
                'Price': buy_price,
                'Shares': position,
                'Value': position * buy_price
            })
        elif df['Position'].iloc[i] == -1 and position > 0:
            sell_price = current_price
            cash = position * sell_price
            profit = (sell_price - buy_price) * position
            profit_pct = ((sell_price / buy_price) - 1) * 100
            position = 0
            trade_log.append({
                'Date': current_date, 
                'Action': 'Sell', 
                'Price': sell_price,
                'Cash': cash,
                'Profit': profit,
                'Profit %': profit_pct
            })
    
    final_value = cash + position * df['y'].iloc[-1]
    profit = final_value - initial_capital
    roi = profit / initial_capital * 100
    
    # Portfolio history DataFrame
    portfolio_df = pd.DataFrame(portfolio_history)
    
    st.markdown("### 📊 Backtesting Performance")
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Initial Capital", f"{initial_capital:,.0f}")
    with col2:
        st.metric("Final Value", f"{final_value:,.0f}")  
    with col3:
        st.metric("Total Return", f"{profit:,.0f}", f"{roi:.2f}%")
    
    if len(portfolio_df) > 0:
        # Portfolio Value Chart
        fig_portfolio = go.Figure()
        fig_portfolio.add_trace(go.Scatter(
            x=portfolio_df['Date'],
            y=portfolio_df['Portfolio Value'],
            mode='lines',
            name='Portfolio Value',
            fill='tozeroy',
            line=dict(color=ACCENT_COLOR, width=2)
        ))
        
        # Buy-and-hold comparison
        shares_buy_hold = initial_capital / df['y'].iloc[1]
        portfolio_df['Buy Hold Value'] = df['y'].iloc[1:].reset_index(drop=True) * shares_buy_hold
        
        fig_portfolio.add_trace(go.Scatter(
            x=portfolio_df['Date'],
            y=portfolio_df['Buy Hold Value'],
            mode='lines',
            name='Buy & Hold',
            line=dict(color=MUTED_COLOR, width=1.5, dash='dash')
        ))
        
        fig_portfolio.update_layout(
            template="plotly_dark",
            plot_bgcolor=BACKGROUND_COLOR,
            paper_bgcolor=BACKGROUND_COLOR,
            font=dict(color=TEXT_COLOR),
            legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=10, b=0),
            hovermode='x unified',
            xaxis=dict(
                showgrid=True,
                gridcolor=CHART_GRIDCOLOR,
                gridwidth=0.5,
                linecolor=CHART_GRIDCOLOR
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_GRIDCOLOR,
                gridwidth=0.5,
                zeroline=False,
                tickformat=',.0f'
            ),
            height=350
        )
        
        st.plotly_chart(fig_portfolio, use_container_width=True)
    
    if trade_log:
        st.markdown("### 🧾 Trade Log")
        trade_df = pd.DataFrame(trade_log)
        trade_df['Date'] = pd.to_datetime(trade_df['Date']).dt.strftime('%Y-%m-%d')
        
        # Add counts and additional metrics
        buy_count = sum(1 for trade in trade_log if trade.get('Action') == 'Buy')
        sell_count = sum(1 for trade in trade_log if trade.get('Action') == 'Sell')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Buy Transactions", buy_count)
        with col2:
            st.metric("Sell Transactions", sell_count)
        
        # Format and display the trade log
        if 'Profit' in trade_df.columns:
            trade_df['Profit'] = trade_df['Profit'].apply(lambda x: f"{x:,.0f}" if not pd.isna(x) else "")
        
        if 'Profit %' in trade_df.columns:
            trade_df['Profit %'] = trade_df['Profit %'].apply(lambda x: f"{x:.2f}%" if not pd.isna(x) else "")
            
        st.dataframe(trade_df, use_container_width=True)
    else:
        st.info("No buy/sell signals were generated in the given time range.")

with tab3:
    st.markdown("### 📘 Technical Analysis Methodology")
    
    st.markdown("""
    <div class="analysis-container">
        <h3>🔍 Moving Average Crossover Strategy</h3>
        <p>
            The primary strategy used in this analysis is the <strong>Moving Average Crossover</strong>, one of the most widely used technical indicators in quantitative finance.
        </p>
        
        <p>
            <strong>How It Works:</strong>
        </p>
        <ul>
            <li>Short-term MA (MA{}) tracks recent price movements</li>
            <li>Long-term MA (MA{}) establishes the overall trend</li>
            <li><strong>Buy Signal:</strong> Short MA crosses above Long MA (bullish momentum)</li>
            <li><strong>Sell Signal:</strong> Short MA crosses below Long MA (bearish momentum)</li>
        </ul>
        
        <p>
            <strong>Current Analysis:</strong><br>
            MA{} is currently <strong>{}</strong> MA{}, suggesting a <strong>{}</strong> signal.
        </p>
    </div>
    
    <div class="analysis-container">
        <h3>🔮 ARIMA Forecasting</h3>
        <p>
            The forecasting model uses <strong>ARIMA</strong> (Autoregressive Integrated Moving Average), a robust statistical time-series method.
        </p>
        
        <p>
            <strong>Key Components:</strong>
        </p>
        <ul>
            <li><strong>AR (p=8):</strong> Uses past values to predict future values</li>
            <li><strong>I (d=1):</strong> Makes the time series stationary through differencing</li>
            <li><strong>MA (q=5):</strong> Accounts for error terms in previous observations</li>
        </ul>
        
        <p>
            <strong>Limitations:</strong> ARIMA models work best with stable, stationary data and may not capture unexpected market events or volatility changes.
        </p>
    </div>
    """.format(
        short_window, long_window,
        short_window, "above" if latest['MA_Short'] > latest['MA_Long'] else "below", long_window,
        "BUY" if latest['Signal'] == 1 else "SELL/HOLD"
    ), unsafe_allow_html=True)
    
    # Risk Assessment
    st.markdown("""
    <div class="analysis-container">
        <h3>⚠️ Risk Assessment</h3>
        <p>
            <strong>Strategy Considerations:</strong>
        </p>
        <ul>
            <li>Moving average strategies can generate false signals in volatile or sideways markets</li>
            <li>There may be a lag in identifying trend changes</li>
            <li>Past performance does not guarantee future results</li>
        </ul>
        
        <p>
            <strong>Recommendation:</strong> Use this analysis as one tool among many in your investment decision process. Consider combining with fundamental analysis and risk management techniques.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- Disclaimer ---
st.markdown("""
<div class="disclaimer-box">
⚠️ <strong>Disclaimer:</strong> This tool is for educational purposes only and does not constitute investment advice. The analysis provided is based on historical data and should not be the sole basis for investment decisions. Past performance is not indicative of future results. Always conduct your own research or consult with a financial advisor before making investment decisions.
</div>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer-text">
    © 2023 Quantum Stock Analysis | Created by Abida Massi
</div>
""", unsafe_allow_html=True)