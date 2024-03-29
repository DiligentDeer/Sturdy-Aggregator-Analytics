import streamlit as st
# import plotly.express as px
import plotly.graph_objects as go
import utils


def instantaneous_data(master_data, asset):
    # Find the row with maximum 'block' value
    max_block_row = master_data.loc[master_data['block'].idxmax()]

    st.write(f"## crvUSD - {asset} Silo")
    st.write(
        f"*Data represented here are up to {utils.block_number_to_date(max_block_row['block'])} UTC*",
        markdown=True)

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
        fig1.update_layout(title='Oracle Low & High (Oracle Low is fetched from Oracle Contract and Oracle High from Pair Contract)', xaxis_title='Block', yaxis_title='Price')
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


def user_position_table(user_table, asset, column):
    # Filter out rows where USDC_LTV is not null
    filtered_table = user_table[user_table[f'{asset}_LTV'].notnull()]

    # Select required columns for the table
    selected_columns_table = ['user', f'{asset}_borrowBalance', f'{asset}_collateralBalance', f'{asset}_LTV',
                              f'{asset}_liq_price']
    filtered_table_table = filtered_table[selected_columns_table]

    # Sort the DataFrame by USDC_LTV
    filtered_table_table = filtered_table_table.sort_values(by=f'{asset}_LTV', ascending=False)

    # Filter out rows where USDC_LTV is not null for the graph
    filtered_table_graph = user_table[user_table[f'{asset}_LTV'].notnull()]

    # Select required columns for the graph
    selected_columns_graph = [f'{asset}_collateralBalance', f'{asset}_liq_price', f'{asset}_share_price']
    filtered_table_graph = filtered_table_graph[selected_columns_graph]

    filtered_table_table = filtered_table_table.rename(columns={
        'user': 'User',
        f'{asset}_borrowBalance': f'Borrow Balance',
        f'{asset}_collateralBalance': f'Collateral Balance',
        f'{asset}_LTV': f'LTV',
        f'{asset}_liq_price': f'Liquidation Price'
    })
    # filtered_table_table = filtered_table_table.rename(columns={
    #     'user': 'User',
    #     f'{asset}_borrowBalance': f'{asset} Borrow Balance',
    #     f'{asset}_collateralBalance': f'{asset} Collateral Balance',
    #     f'{asset}_LTV': f'{asset} LTV',
    #     f'{asset}_liq_price': f'{asset} Share Price'
    # })

    # Add a heading for the table
    column.markdown(f"#### {asset} Silo - User Positions")

    # Display the table without index
    column.write(filtered_table_table, index=False)


def position_risk_chart(filtered_table_graph, asset, column):
    with column:
        # Create a new Plotly figure
        fig = go.Figure()

        # Add scatter trace (scatter plot)
        fig.add_trace(go.Scatter(
            x=filtered_table_graph[f'{asset}_liq_price'],
            y=filtered_table_graph[f'{asset}_collateralBalance'],
            mode='markers',  # Display markers only
            name=f'{asset} Collateral Balance',
            marker=dict(color='blue', size=10)  # Set marker color and size
        ))

        # Add vertical line at the 'USDC_share_price' value
        share_price_value = filtered_table_graph[f'{asset}_share_price'].iloc[
            0]  # Assuming 'USDC_share_price' has only one value
        fig.add_shape(
            type="line",
            x0=share_price_value,
            y0=0,
            x1=share_price_value,
            y1=max(filtered_table_graph[f'{asset}_collateralBalance']),
            line=dict(
                color="#6ac69b",
                width=1,
                dash="dash",
            )
        )

        # Add annotation for the value of the yellow line
        fig.add_annotation(
            x=share_price_value,
            y=max(filtered_table_graph[f'{asset}_collateralBalance']),
            text=f"{asset} silo share price: {share_price_value:.4f}",
            showarrow=True,
            arrowcolor='#6ac69b',
            arrowhead=0,
            ax=0,
            ay=-20
        )

        # Update layout
        fig.update_layout(
            title=f"{asset} Silo - User Collateral Balance vs. {asset} Silo Share Price",
            xaxis_title=f"{asset} Share Price",
            yaxis_title=f"{asset} Collateral Balance",
            xaxis=dict(
                range=[0.8, 2]  # Set the range of x-axis to no more than 2
            )
        )

        st.plotly_chart(fig)