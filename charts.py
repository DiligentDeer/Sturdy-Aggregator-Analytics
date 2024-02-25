import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def instantaneous_data(master_data, asset):
    st.write(f"## crvUSD - {asset} Silo")
    ##################################
    # Find the row with maximum 'block' value
    max_block_row = master_data.loc[master_data['block'].idxmax()]

    # Create a layout with three columns
    col1, col2, col3 = st.columns(3)

    # Display data counters in each column
    with col1:
        st.write(f"#### Usage Metrics for block: {max_block_row['block']:.0f}")
        st.write(f"**Reserve Size:** {max_block_row[f'reserveSize{asset}']:.4f} crvUSD")
        st.write(f"**Current Borrow:** {max_block_row[f'currentBorrow{asset}']:.4f} crvUSD")
        st.write(f"**Utilization:** {max_block_row[f'utilization{asset}'] * 100:.4f} %")

    with col2:
        st.write(f"#### Rate Metrics for block: {max_block_row['block']:.0f}")
        st.write(f"**Collateral APR:** {max_block_row[f'collateralApr_{asset}'] * 100:.4f} %")
        st.write(f"**Borrow APY:** {max_block_row[f'borrowApy_{asset}'] * 100:.4f} %")
        st.write(f"**Lend APY:** {max_block_row[f'supplyApy_{asset}'] * 100:.4f} %")

    with col3:
        st.write(f"#### Oracle Data for block: {max_block_row['block']:.0f}")
        st.write(f"**Oracle Low:** {max_block_row[f'oracleLow{asset}']:.4f} ")
        st.write(f"**Oracle high:** {max_block_row[f'oracleHigh{asset}']:.4f} ")
        st.write(f"**Normalized:** {max_block_row[f'oracleNormalized{asset}']:.4f}")


def usage_metrics(master_data, asset):
    fig = go.Figure()

    # Add traces for 'reserveSizeUSDC' and 'currentBorrowUSDC' as area charts on the left y-axis
    fig.add_trace(go.Scatter(x=master_data['block'], y=master_data[f'reserveSize{asset}'],
                             mode='lines+markers', fill='tozeroy', name='Reserve Size',
                             yaxis='y', line=dict(color='#6ac69b'), fillcolor='rgba(106, 198, 155, 0.3)'))
    fig.add_trace(go.Scatter(x=master_data['block'], y=master_data[f'currentBorrow{asset}'],
                             mode='lines+markers', fill='tozeroy', name='Current Borrow',
                             yaxis='y', line=dict(color='#127475'), fillcolor='rgba(18, 116, 117, 0.3)'))

    # Add trace for 'utilizationUSDC' * 100% on the right y-axis
    fig.add_trace(go.Scatter(x=master_data['block'], y=master_data[f'utilization{asset}'] * 100,
                             mode='lines', name='Utilization', yaxis='y2',
                             line=dict(color='#252525')))

    # Update layout with titles and axis labels
    fig.update_layout(
        title=f'crvUSD-{asset} Silo Usage Metrics',
        xaxis_title='Block',
        yaxis_title='# of crvUSD',
        yaxis2=dict(
            title='Utilization (%)',
            overlaying='y',
            side='right'
        )
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def misc_charts(master_data, asset):
    # Set up a two-column layout with wider columns
    left_column, right_column = st.columns(2)

    # First line chart in the left column
    with left_column:
        # Specify the y-axis columns for the first line chart
        y_columns_1 = [f'collateralApr_{asset}', f'borrowApy_{asset}']  # Predefined columns
        fig1 = go.Figure()
        colors = ['#127475', '#6ac69b']  # Custom colors
        for i, column in enumerate(y_columns_1):
            fig1.add_trace(
                go.Scatter(x=master_data['block'], y=master_data[column] * 100, name=column,
                           line=dict(color=colors[i])))
        fig1.update_layout(title='Collateral returns vs Borrow interest rate', xaxis_title='Block', yaxis_title='(%)')
        fig1.update_layout(legend=dict(title='Legend'))  # Add legend title
        st.plotly_chart(fig1, use_container_width=True)  # Adjust width to container width

    # Second line chart in the right column
    with right_column:
        # Specify the y-axis columns for the second line chart
        y_columns_2 = [f'supplyApy_{asset}', f'borrowApy_{asset}']  # Predefined columns
        fig2 = go.Figure()
        for i, column in enumerate(y_columns_2):
            fig2.add_trace(
                go.Scatter(x=master_data['block'], y=master_data[column] * 100, name=column,
                           line=dict(color=colors[i])))
        fig2.update_layout(title='Lending returns vs Borrow interest rate', xaxis_title='Block', yaxis_title='(%)')
        fig2.update_layout(legend=dict(title='Legend'))  # Add legend title
        st.plotly_chart(fig2, use_container_width=True)  # Adjust width to container width

    with left_column:
        # Specify the y-axis columns for the first line chart
        y_columns_1 = [f'oracleLow{asset}', f'oracleHigh{asset}']  # Predefined columns
        fig1 = go.Figure()
        colors = ['#127475', '#6ac69b']  # Custom colors
        for i, column in enumerate(y_columns_1):
            fig1.add_trace(
                go.Scatter(x=master_data['block'], y=master_data[column], name=column, line=dict(color=colors[i])))
        fig1.update_layout(title='Oracle Low & High', xaxis_title='Block', yaxis_title='Price')
        fig1.update_layout(legend=dict(title='Legend'))  # Add legend title
        st.plotly_chart(fig1, use_container_width=True)  # Adjust width to container width

    # Second line chart in the right column
    with right_column:
        # Specify the y-axis columns for the second line chart
        y_columns_2 = [f'oracleNormalized{asset}']  # Predefined columns
        fig2 = go.Figure()
        for i, column in enumerate(y_columns_2):
            fig2.add_trace(
                go.Scatter(x=master_data['block'], y=master_data[column], name=column, line=dict(color=colors[i])))
        fig2.update_layout(title='Normalized Oracle', xaxis_title='Block', yaxis_title='Price')
        fig2.update_layout(legend=dict(title='Legend'))  # Add legend title
        st.plotly_chart(fig2, use_container_width=True)  # Adjust width to container width