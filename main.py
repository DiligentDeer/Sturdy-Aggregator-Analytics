import streamlit as st

import utils
import charts
import const

# LOAD past saved files
saved_strategy_data, saved_pps_data = utils.load_data()

# Get the latest Block Number to check if enough time has passed to accumulate data for new Blocks
latest_block_with_data = saved_strategy_data['block'].max()

historic_block_list = utils.accumulate_block_with_no_data(latest_block_with_data)

if utils.w3.eth.block_number - const.BLOCK_INTERVAL > latest_block_with_data:
    saved_strategy_data, saved_pps_data = utils.get_data_for_blocks(historic_block_list, saved_strategy_data, saved_pps_data)

master_data = utils.compute_master_data(utils.process_dataframe(saved_pps_data), saved_strategy_data)

print(master_data)
master_data.info()

# Set the layout width to a wider size
st.set_page_config(layout="wide")

# Add title to your Streamlit app
st.title('Sturdy crvUSD Aggregator Silo Data')

for i in range(len(const.STRATEGY_NAME)):
    charts.instantaneous_data(master_data, const.STRATEGY_NAME[i])
    charts.usage_metrics(master_data, const.STRATEGY_NAME[i])
    charts.misc_charts(master_data, const.STRATEGY_NAME[i])