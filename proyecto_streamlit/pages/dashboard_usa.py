import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# Portfolio details
portfolio_usa = ['BABA', 'ACN', 'PDD', 'BIDU', 'NKE', 'DAVA', 'VOO', 'QQQ', 'SPYG']
shares_owned_usa = {
    'BABA': 3.6717,
    'ACN': 0.44484,
    'PDD': 2.11386,
    'BIDU': 0.45074,
    'NKE': 1.09433,
    'DAVA': 3.20205,
    'VOO': 2,
    'QQQ': 1.1556,
    'SPYG': 1
}
purchase_prices_usa = {
    'BABA': 81.74,
    'ACN': 292.24,
    'PDD': 141.92,
    'BIDU': 110.93,
    'NKE': 91.38,
    'DAVA': 31.23,
    'VOO': 471.11,
    'QQQ': 444.92,
    'SPYG': 72.43
}

# Helper functions
def download_data(tickers):
    try:
        data = yf.download(tickers, period='1d')['Adj Close']
        return data if not data.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def create_donut_chart(df, title):
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', 
              '#858796', '#f8f9fc', '#5a5c69', '#2e59d9', '#17a673']
    
    fig = go.Figure(data=[go.Pie(
        labels=df['Ticker'],
        values=df['Current Value (USD)'],
        hole=.7,
        textinfo='label+percent',
        marker=dict(colors=colors[:len(df)])
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
    st.set_page_config(page_title="USA Portfolio Analysis", layout="wide")
    
    # Title
    st.title("USA Portfolio Analysis")
    
    # Download and process data
    current_prices_usa = download_data(portfolio_usa)

    if current_prices_usa.empty:
        st.error("Error loading data. Please try again later.")
        return

    # Process portfolio data
    portfolio_data = []
    for ticker in portfolio_usa:
        shares = shares_owned_usa[ticker]
        purchase_price = purchase_prices_usa[ticker]
        current_price = current_prices_usa[ticker].iloc[0] if ticker in current_prices_usa else 0
        invested_value = shares * purchase_price
        current_value = shares * current_price
        performance = ((current_value / invested_value) - 1) * 100 if invested_value > 0 else 0

        portfolio_data.append({
            'Ticker': ticker,
            'Shares Owned': f"{shares:,.2f}",
            'Purchase Price (USD)': f"${purchase_price:.2f}",
            'Current Price (USD)': f"${current_price:.2f}",
            'Invested Value (USD)': invested_value,
            'Current Value (USD)': current_value,
            'Performance (%)': performance
        })

    df = pd.DataFrame(portfolio_data)
    
    # Calculate totals
    total_invested = df['Invested Value (USD)'].sum()
    total_current = df['Current Value (USD)'].sum()
    total_performance = ((total_current / total_invested) - 1) * 100 if total_invested > 0 else 0

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
    
    # Add styling to the dataframe
    def color_performance(val):
        val = float(val.strip('%'))
        color = '#1cc88a' if val >= 0 else '#e74a3b'
        return f'color: {color}; font-weight: bold'
    
    styled_df = display_df.style.applymap(color_performance, subset=['Performance (%)'])
    st.dataframe(styled_df, use_container_width=True)

if __name__ == "__main__":
    main()