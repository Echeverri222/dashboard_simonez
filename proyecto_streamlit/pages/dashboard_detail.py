import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import numpy as np

# Portfolio symbols and positions data
portfolio = ['BABA', 'ACN', 'PDD', 'BIDU', 'NKE', 'DAVA', 'VOO', 'QQQ', 'SPYG', '1211.HK', '0700.HK']

positions = {
    'VOO': [
        {'shares': 0.48222, 'price': 455.80, 'date': '2024-02-20'},
        {'shares': 1.51778, 'price': 475.97, 'date': '2024-03-08'}
    ],
    'QQQ': [
        {'shares': 0.11396, 'price': 438.19, 'date': '2024-02-29'},
        {'shares': 0.88604, 'price': 447.66, 'date': '2024-03-08'},
        {'shares': 0.1556, 'price': 434.25, 'date': '2024-03-15'}
    ]
}

# Add entries for stocks with a single purchase
positions.update({
    'BABA': [{'shares': 3.6717, 'price': 81.74, 'date': '2024-05-06'}],
    'ACN': [{'shares': 0.44484, 'price': 292.24, 'date': '2024-06-06'}],
    'PDD': [{'shares': 2.11386, 'price': 141.92, 'date': '2024-05-16'}],
    'BIDU': [{'shares': 0.45074, 'price': 110.9287, 'date': '2024-05-17'}],
    'NKE': [{'shares': 1.09433, 'price': 91.38, 'date': '2024-05-13'}],
    'DAVA': [{'shares': 3.20205, 'price': 31.23, 'date': '2024-05-17'}],
    'SPYG': [{'shares': 1, 'price': 72.43, 'date': '2024-03-13'}],
    '1211.HK': [{'shares': 6.91, 'price': 226, 'date': '2024-05-05'}],
    '0700.HK': [{'shares': 0.98, 'price': 399.60, 'date': '2022-04-01'}]
})

# Helper functions
def download_data(ticker, period='1y'):
    try:
        data = yf.download(ticker, period=period)
        return data if not data.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def create_price_chart(data, ticker):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Adj Close'],
        mode='lines',
        name='Price',
        line=dict(color='#4e73df')
    ))
    
    fig.update_layout(
        title=f'Historical Price of {ticker}',
        margin=dict(t=30, b=0, l=0, r=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Price (USD)",
        showlegend=False
    )
    return fig

def create_comparison_chart(data, ticker):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Invested Value',
        x=[ticker],
        y=[data['Invested Value ($)']],
        marker_color='#4e73df',
    ))
    
    fig.add_trace(go.Bar(
        name='Current Value',
        x=[ticker],
        y=[data['Current Value ($)']],
        marker_color='#1cc88a',
    ))
    
    fig.update_layout(
        title=f'Invested vs Current Value for {ticker}',
        barmode='group',
        margin=dict(t=30, b=0, l=0, r=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="USD",
        showlegend=True,
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
    st.set_page_config(page_title="Detailed Portfolio Analysis", layout="wide")
    
    # Title
    st.title("Detailed Portfolio Analysis")
    
    # Select a stock
    selected_ticker = st.selectbox("Select a Stock for Analysis:", portfolio)
    
    # Download data
    historical_data = download_data(selected_ticker)
    spy_data = download_data('SPY')
    
    if historical_data.empty or spy_data.empty:
        st.error("Error loading data. Please try again later.")
        return

    # Calculate total shares and values
    total_shares = sum([pos['shares'] for pos in positions[selected_ticker]])
    total_invested = sum([pos['shares'] * pos['price'] for pos in positions[selected_ticker]])
    current_price = historical_data['Adj Close'].iloc[-1]
    current_value = total_shares * current_price
    performance = ((current_value / total_invested) - 1) * 100

    # Prepare stock details data
    stock_data = []
    for pos in positions[selected_ticker]:
        current_value_pos = pos['shares'] * current_price
        invested_value_pos = pos['shares'] * pos['price']
        performance_pos = ((current_value_pos / invested_value_pos) - 1) * 100
        
        stock_data.append({
            'Purchase Date': pos['date'],
            'Shares': f"{pos['shares']:,.4f}",
            'Purchase Price (USD)': f"${pos['price']:.2f}",
            'Current Price (USD)': f"${current_price:.2f}",
            'Invested Value (USD)': f"${invested_value_pos:,.2f}",
            'Current Value (USD)': f"${current_value_pos:,.2f}",
            'Performance (%)': f"{performance_pos:.2f}%"
        })

    df = pd.DataFrame(stock_data)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"${total_invested:,.2f}")
    with col2:
        st.metric("Current Value", f"${current_value:,.2f}")
    with col3:
        st.metric("Performance", f"{performance:.2f}%", delta=f"{performance:.2f}%")

    # Charts section
    st.subheader("Portfolio Analysis")
    tab1, tab2 = st.tabs(["Historical Price", "Investment Comparison"])
    
    with tab1:
        st.plotly_chart(create_price_chart(historical_data, selected_ticker), use_container_width=True)
    with tab2:
        comparison_data = pd.DataFrame({
            'Ticker': [selected_ticker],
            'Invested Value ($)': [total_invested],
            'Current Value ($)': [current_value]
        })
        st.plotly_chart(create_comparison_chart(comparison_data.iloc[0], selected_ticker), use_container_width=True)
    
    # Portfolio details table
    st.subheader("Stock Details")
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
