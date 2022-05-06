import pandas as pd
import streamlit as st
import plotly.express as px
from LARPlib.oracle import ftx as ftx

@st.experimental_memo
def get_data():
    tickers = ftx.get_tickers()
    df, instruments = ftx.get_historical_df(tickers)
    cumret = ftx.get_historical_cumret(df, tickers=instruments)
    return cumret

def calculate_spread(first_pair, second_pair, cumret):
    spread = cumret[first_pair] - cumret[second_pair]
    spread_mean = spread.mean() # historical mean
    spread_std = spread.std() # historical standard deviation
    return spread, spread_mean, spread_std


def main():
    # Use the full page instead of a narrow central column
    st.set_page_config(
        page_title="LARPboard",
        page_icon="clown",
        layout="wide"
    )
    
    st.title('🤡 LARPboard')

    tickers = ftx.get_tickers()
    
    # metrics
    col1, col2, col3 = st.columns(3)
    col1.metric('Regime Shift Indicator', 'Mean-reverting', '69420')
    col2.metric('Hurst Exponent', 'Some number', '+10')
    col3.metric('CADF', '69', '-20')

    # choose pairs
    pair_choice_expander = st.expander(label="Choose your pairs")
    with pair_choice_expander:
        first, second = st.columns(2)
        first_pair = first.selectbox('Choose one', tickers)
        first_pair = first_pair[:first_pair.find('-')]
        second_pair = second.selectbox('Choose another one', tickers)
        second_pair = second_pair[:second_pair.find('-')]
        st.multiselect('Metrics', ['CADF', 'Hurst Exponent', 'Portmanteau', 'Half Life', 'Zero-Crossings', 'KPSS'])
        
    st.write(f'You selected {first_pair} and {second_pair}')

    # get data and plot it
    cumret = get_data()
    spread, mu, sigma = calculate_spread(first_pair, second_pair, cumret)

    fig = px.line(spread, title=f"{first_pair}-{second_pair} spread")
    fig.add_hline(
        y = mu,
        line_dash = 'dot',
        line_width = 3,
        line_color = 'green',
        annotation_text = 'mean',
        annotation_position = 'bottom right'
    )
    fig.add_hline(
        y = mu + 2 * sigma,
        line_dash = 'dash',
        line_width = 3,
        line_color = 'red',
        annotation_text = '2 std dev',
        annotation_position = 'bottom right'
    )
    fig.add_hline(
        y = mu - 2 * sigma,
        line_dash = 'dash',
        line_width = 3,
        line_color = 'red',
        annotation_text = '2 std dev',
        annotation_position = 'top right'
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()