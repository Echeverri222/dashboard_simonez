import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

# Portfolio details
portfolio_hk = ['1211.HK', '0700.HK']
shares_owned_hk = {'1211.HK': 6.91, '0700.HK': 0.98}
purchase_prices_hk = {'1211.HK': 226, '0700.HK': 399.60}

# Helper functions
def download_data(tickers):
    try:
        data = yf.download(tickers, period='1d')['Adj Close']
        return data if not data.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_fx_rate():
    try:
        fx_data = yf.download('HKD=X', period='1d')
        fx_rate_usd_to_hkd = fx_data['Adj Close'].iloc[0] if not fx_data.empty else 7.85
        return 1 / fx_rate_usd_to_hkd
    except Exception:
        return 0.128

def create_donut_chart(df, title):
    fig = go.Figure(data=[go.Pie(
        labels=df['Ticker'],
        values=df['Current Value (USD)'],
        hole=.7,
        textinfo='label+percent',
        marker=dict(colors=['#4e73df', '#1cc88a'])
    )])
    
    fig.update_layout(
        title=title,
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_performance_chart(df):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Ticker'],
        y=df['Performance (%)'],
        marker_color=['#4e73df' if val >= 0 else '#e74a3b' for val in df['Performance (%)']],
        text=[f"{val:.1f}%" for val in df['Performance (%)']],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Performance by Stock',
        margin=dict(t=30, b=0, l=0, r=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Performance (%)",
        showlegend=False
    )
    return fig

def create_value_comparison_chart(df):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Invested Value',
        x=df['Ticker'],
        y=df['Invested Value (USD)'],
        marker_color='#4e73df',
    ))
    
    fig.add_trace(go.Bar(
        name='Current Value',
        x=df['Ticker'],
        y=df['Current Value (USD)'],
        marker_color='#1cc88a',
    ))
    
    fig.update_layout(
        title='Invested vs Current Value',
        barmode='group',
        margin=dict(t=30, b=0, l=0, r=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="USD",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def main():
    st.set_page_config(page_title="Hong Kong Portfolio Analysis", layout="wide")
    
    # Title
    st.title("Hong Kong Portfolio Analysis")
    
    # Download and process data
    current_prices_hk = download_data(portfolio_hk)
    fx_rate_hkd_to_usd = get_fx_rate()

    if current_prices_hk.empty:
        st.error("Error loading data. Please try again later.")
        return

    # Process portfolio data
    portfolio_data = []
    for ticker in portfolio_hk:
        shares = shares_owned_hk[ticker]
        purchase_price_usd = purchase_prices_hk[ticker] * fx_rate_hkd_to_usd
        current_price_usd = current_prices_hk[ticker].iloc[0] * fx_rate_hkd_to_usd
        invested_value = shares * purchase_price_usd
        current_value = shares * current_price_usd
        performance = ((current_value / invested_value) - 1) * 100

        portfolio_data.append({
            'Ticker': ticker,
            'Shares Owned': f"{shares:,.2f}",
            'Purchase Price (USD)': f"${purchase_price_usd:.2f}",
            'Current Price (USD)': f"${current_price_usd:.2f}",
            'Invested Value (USD)': invested_value,
            'Current Value (USD)': current_value,
            'Performance (%)': performance
        })

    df = pd.DataFrame(portfolio_data)
    
    # Calculate totals
    total_invested = df['Invested Value (USD)'].sum()
    total_current = df['Current Value (USD)'].sum()
    total_performance = ((total_current / total_invested) - 1) * 100

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"${total_invested:,.2f}")
    with col2:
        st.metric("Current Value", f"${total_current:,.2f}")
    with col3:
        st.metric("Performance", f"{total_performance:,.2f}%", 
                 delta=f"{total_performance:,.2f}%")

    # Charts section
    st.subheader("Portfolio Analysis")
    tab1, tab2, tab3 = st.tabs(["Portfolio Distribution", 
                               "Performance", 
                               "Value Comparison"])
    
    with tab1:
        st.plotly_chart(create_donut_chart(df, "Portfolio Distribution"), 
                       use_container_width=True)
    with tab2:
        st.plotly_chart(create_performance_chart(df), 
                       use_container_width=True)
    with tab3:
        st.plotly_chart(create_value_comparison_chart(df), 
                       use_container_width=True)

    # Portfolio details table
    st.subheader("Portfolio Details")
    
    # Format numeric columns for display
    display_df = df.copy()
    display_df['Invested Value (USD)'] = display_df['Invested Value (USD)'].apply(lambda x: f"${x:,.2f}")
    display_df['Current Value (USD)'] = display_df['Current Value (USD)'].apply(lambda x: f"${x:,.2f}")
    display_df['Performance (%)'] = display_df['Performance (%)'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main()