import streamlit as st # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import pandas as pd # type: ignore
import yfinance as yf # type: ignore
import numpy as np # type: ignore

# Set page config
st.set_page_config(
    page_title="Investment Portfolio",
    page_icon="📈",
    layout="wide"
)

# Add custom CSS to center content
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 5% 5% 5% 10%;
        border-radius: 5px;
        color: rgb(30, 103, 119);
        overflow-wrap: break-word;
    }

    /* breakline for metric text         */
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
        overflow-wrap: break-word;
        white-space: break-spaces;
        color: rgb(49, 51, 63);
    }

    /* Hide deployment button */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Portfolio data
portfolio_hk = ['1211.HK', '0700.HK']
portfolio_usa = ['BABA', 'ACN', 'PDD', 'BIDU', 'NKE', 'DAVA', 'VOO', 'QQQ', 'SPYG']
shares_owned_hk = {'1211.HK': 6.91, '0700.HK': 0.98}
shares_owned_usa = {
    'BABA': 3.6717, 'ACN': 0.44484, 'PDD': 2.11386, 'BIDU': 0.45074,
    'NKE': 1.09433, 'DAVA': 3.20205, 'VOO': 2, 'QQQ': 1.1556, 'SPYG': 1
}
purchase_prices_hk = {'1211.HK': 226, '0700.HK': 399.60}
purchase_prices_usa = {
    'BABA': 81.74, 'ACN': 292.24, 'PDD': 141.92, 'BIDU': 110.93,
    'NKE': 91.38, 'DAVA': 31.23, 'VOO': 471.11, 'QQQ': 444.92, 'SPYG': 72.43
}
cash_available = 77.77
sales_data = [
    {
        'Ticker': '9618.HK',
        'Cantidad Vendida': 2.84,
        'Precio de Compra (HKD)': 137.3,
        'Precio de Venta (HKD)': 184.32,
        'Monto Total Venta (HKD)': 2.84 * 184.32
    }
]

# Helper functions
@st.cache_data(ttl=3600)
def download_data(tickers):
    try:
        data = yf.download(tickers, period='1d')['Adj Close']
        if data.empty:
            st.warning(f"No data available for some tickers: {tickers}")
        return data
    except Exception as e:
        st.error(f"Error downloading data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_fx_rate():
    try:
        fx_data = yf.download('HKD=X', period='1d')
        if not fx_data.empty and 'Adj Close' in fx_data.columns:
            return 1 / fx_data['Adj Close'].iloc[-1]
        return None
    except Exception:
        return None

def create_donut_chart(data, labels, title):
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=data,
        hole=.7,
        textinfo='label+percent',
        marker=dict(colors=['#4e73df', '#1cc88a', '#36b9cc'])
    )])
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_bar_chart(x_data, y_data, title):
    fig = go.Figure(data=[
        go.Bar(
            x=x_data,
            y=y_data,
            marker_color=['#4e73df', '#1cc88a'],
            text=[f"{y:.1f}%" for y in y_data],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=title,
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Rentabilidad (%)",
        showlegend=False
    )
    return fig

# Calculate portfolio values
current_prices_hk = download_data(portfolio_hk)
current_prices_usa = download_data(portfolio_usa)
fx_rate_hkd_to_usd = get_fx_rate() or 0.128

def calculate_portfolio_metrics():
    try:
        # Calculate HK portfolio values with error handling
        total_invested_value_hk_usd = sum(
            shares_owned_hk[ticker] * purchase_prices_hk[ticker] * fx_rate_hkd_to_usd 
            for ticker in portfolio_hk
        )
        
        total_current_value_hk_usd = 0
        for ticker in portfolio_hk:
            try:
                price = current_prices_hk[ticker]
                if isinstance(price, pd.Series) and not price.empty:
                    current_price = price.iloc[-1]
                else:
                    current_price = price
                total_current_value_hk_usd += shares_owned_hk[ticker] * current_price * fx_rate_hkd_to_usd
            except (IndexError, AttributeError, KeyError):
                st.warning(f"Failed to get current price for {ticker}. Using purchase price instead.")
                total_current_value_hk_usd += shares_owned_hk[ticker] * purchase_prices_hk[ticker] * fx_rate_hkd_to_usd
        
        # Calculate USA portfolio values with error handling
        total_invested_value_usa = sum(
            shares_owned_usa[ticker] * purchase_prices_usa[ticker] 
            for ticker in portfolio_usa
        )
        
        total_current_value_usa = 0
        for ticker in portfolio_usa:
            try:
                price = current_prices_usa[ticker]
                if isinstance(price, pd.Series) and not price.empty:
                    current_price = price.iloc[-1]
                else:
                    current_price = price
                total_current_value_usa += shares_owned_usa[ticker] * current_price
            except (IndexError, AttributeError, KeyError):
                st.warning(f"Failed to get current price for {ticker}. Using purchase price instead.")
                total_current_value_usa += shares_owned_usa[ticker] * purchase_prices_usa[ticker]
        
        # Calculate performance metrics with safeguards against division by zero
        performance_hk = 0 if total_invested_value_hk_usd == 0 else (
            (total_current_value_hk_usd / total_invested_value_hk_usd - 1) * 100
        )
        
        performance_usa = 0 if total_invested_value_usa == 0 else (
            (total_current_value_usa / total_invested_value_usa - 1) * 100
        )
        
        return {
            'total_invested': total_invested_value_hk_usd + total_invested_value_usa,
            'total_current_hk': total_current_value_hk_usd,
            'total_current_usa': total_current_value_usa,
            'total_current': total_current_value_hk_usd + total_current_value_usa,
            'performance_hk': performance_hk,
            'performance_usa': performance_usa
        }
    except Exception as e:
        st.error(f"Error calculating portfolio metrics: {str(e)}")
        # Return default values in case of error
        return {
            'total_invested': 0,
            'total_current_hk': 0,
            'total_current_usa': 0,
            'total_current': 0,
            'performance_hk': 0,
            'performance_usa': 0
        }

# Calculate metrics
metrics = calculate_portfolio_metrics()

# Main app
st.title("Investment Portfolio Overview")

# Add page navigation info in the sidebar
st.sidebar.title("Navigation")
st.sidebar.info("""
### Available Pages:
- Current: General Overview
- HK Market Details
- US Market Analysis
- Detailed Portfolio Stats

Use the menu above to navigate between pages.
""")

# Create a container for better width control
container = st.container()
with container:
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create columns with specific widths to center the metrics
    left_spacer, col1, col2, col3, col4, right_spacer = st.columns([0.5, 1, 1, 1, 1, 0.5])

    with col1:
        st.metric(
            "Total Return",
            f"{(((metrics['total_current'].sum() if isinstance(metrics['total_current'], pd.Series) else metrics['total_current']) / (metrics['total_invested'].sum() if isinstance(metrics['total_invested'], pd.Series) else metrics['total_invested'])) - 1) * 100:.2f}%",
            delta=None
        )

    with col2:
        st.metric(
            "Total Investment",
            f"${metrics['total_invested']:,.2f}",
            delta=None
        )

    with col3:
        st.metric(
            "Current Value",
            f"${(metrics['total_current'] + cash_available):,.2f}",
            delta=None
        )

    with col4:
        st.metric(
            "Available Cash",
            f"${cash_available:.2f}",
            delta=None
        )

    # Add some spacing after the metrics
    st.markdown("<br>", unsafe_allow_html=True)

# Charts
chart_container = st.container()
with chart_container:
    col1, col2 = st.columns(2)

    with col1:
        donut_chart = create_donut_chart(
            [metrics['total_current_hk'], metrics['total_current_usa'], cash_available],
            ['Hong Kong', 'USA', 'Cash'],
            'Portfolio Distribution'
        )
        st.plotly_chart(donut_chart, use_container_width=True)

    with col2:
        bar_chart = create_bar_chart(
            ['Hong Kong', 'USA'],
            [metrics['performance_hk'], metrics['performance_usa']],
            'Performance by Market'
        )
        st.plotly_chart(bar_chart, use_container_width=True)

# Sales table
sales_container = st.container()
with sales_container:
    st.subheader("Sales Record")

    # Process sales data for the table
    sales_df = pd.DataFrame(sales_data)
    sales_df['Monto Total Venta (USD)'] = sales_df['Monto Total Venta (HKD)'] * fx_rate_hkd_to_usd
    sales_df['Rentabilidad Venta (%)'] = (
        (sales_df['Monto Total Venta (HKD)'] / 
         (sales_df['Precio de Compra (HKD)'] * sales_df['Cantidad Vendida']) - 1) * 100
    ).round(2)

    # Center the table using columns
    left_spacer, table_col, right_spacer = st.columns([0.1, 0.8, 0.1])
    
    with table_col:
        st.dataframe(
            sales_df,
            column_config={
                'Monto Total Venta (USD)': st.column_config.NumberColumn(
                    'Total (USD)',
                    format="$%.2f"
                ),
                'Rentabilidad Venta (%)': st.column_config.NumberColumn(
                    'Return',
                    format="%.2f%%"
                )
            },
            hide_index=True,
            use_container_width=True
        )

# Add last update timestamp
st.sidebar.markdown("---")
st.sidebar.write("Last updated:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))