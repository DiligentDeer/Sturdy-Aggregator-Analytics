from web3 import Web3, HTTPProvider
import const
import pandas as pd
import streamlit as st

w3 = Web3(HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/B3A-qCm7fnjB-pxRDlEq1-iJyOIY54-Z"))



def accumulate_block_with_no_data(latest_block_with_data):
    latest_block_number = w3.eth.block_number
    historic_block_list = []

    start_block_number = closest_lower_value(latest_block_with_data) + const.BLOCK_INTERVAL
    # print(f'start_block_number = {start_block_number}')

    while start_block_number < latest_block_number:
        # Add the current block number to the list
        historic_block_list.append(start_block_number)
        # Compute the next block number
        start_block_number += const.BLOCK_INTERVAL

    historic_block_list.append(latest_block_number)

    return historic_block_list


def closest_lower_value(latest_block_with_data, starting_number=const.BLOCK_START):
    # print(f'starting_number = {starting_number}')
    target_number = latest_block_with_data
    # Calculate the number of steps needed to reach the target number
    steps = (target_number - starting_number) // 1200

    # Calculate the closest lower value
    closest_lower = starting_number + steps * 1200

    return closest_lower


# Strategy Pair Calls
def pair_call_interest(address, block):
    # Convert the address to checksum format
    pair_address = Web3.to_checksum_address(address)

    # ABI for the pricePerShare function
    function_abi = [{"inputs": [], "name": "previewAddInterest",
                     "outputs": [{"internalType": "uint256", "name": "_interestEarned", "type": "uint256"},
                                 {"internalType": "uint256", "name": "_feesAmount", "type": "uint256"},
                                 {"internalType": "uint256", "name": "_feesShare", "type": "uint256"}, {
                                     "components": [{"internalType": "uint32", "name": "lastBlock", "type": "uint32"},
                                                    {"internalType": "uint32", "name": "feeToProtocolRate",
                                                     "type": "uint32"},
                                                    {"internalType": "uint64", "name": "lastTimestamp",
                                                     "type": "uint64"},
                                                    {"internalType": "uint64", "name": "ratePerSec", "type": "uint64"},
                                                    {"internalType": "uint64", "name": "fullUtilizationRate",
                                                     "type": "uint64"}],
                                     "internalType": "struct SturdyPairCore.CurrentRateInfo",
                                     "name": "_newCurrentRateInfo", "type": "tuple"}, {
                                     "components": [{"internalType": "uint128", "name": "amount", "type": "uint128"},
                                                    {"internalType": "uint128", "name": "shares", "type": "uint128"}],
                                     "internalType": "struct VaultAccount", "name": "_totalAsset", "type": "tuple"}, {
                                     "components": [{"internalType": "uint128", "name": "amount", "type": "uint128"},
                                                    {"internalType": "uint128", "name": "shares", "type": "uint128"}],
                                     "internalType": "struct VaultAccount", "name": "_totalBorrow", "type": "tuple"}],
                     "stateMutability": "view", "type": "function"}]

    # Contract instance for the provided address and ABI
    contract = w3.eth.contract(address=pair_address, abi=function_abi)

    # Call the pricePerShare function with the provided block
    newCurrentRateInfo = contract.functions.previewAddInterest().call(block_identifier=int(block))

    # Extract the value inside _newCurrentRateInfo[3]
    rate_per_sec = newCurrentRateInfo[3][3]

    return rate_per_sec


def pair_call_feerate(address, block):
    # Convert the address to checksum format
    pair_address = Web3.to_checksum_address(address)

    # ABI for the currentRateInfo function
    function_abi = [{"inputs": [], "name": "currentRateInfo",
                     "outputs": [{"internalType": "uint32", "name": "lastBlock", "type": "uint32"},
                                 {"internalType": "uint32", "name": "feeToProtocolRate", "type": "uint32"},
                                 {"internalType": "uint64", "name": "lastTimestamp", "type": "uint64"},
                                 {"internalType": "uint64", "name": "ratePerSec", "type": "uint64"},
                                 {"internalType": "uint64", "name": "fullUtilizationRate", "type": "uint64"}],
                     "stateMutability": "view", "type": "function"}]

    # Contract instance for the provided address and ABI
    contract = w3.eth.contract(address=pair_address, abi=function_abi)

    # Call the currentRateInfo function with the provided block
    current_rate_info = contract.functions.currentRateInfo().call(block_identifier=int(block))

    # Extract the value of feeToProtocolRate from the tuple
    fee_to_protocol_rate = current_rate_info[1]

    return fee_to_protocol_rate


# Yearn Calls
def fetch_pps(address, block):
    # Convert the address to checksum format
    yearn_address = Web3.to_checksum_address(address)

    # ABI for the pricePerShare function
    pricePerShare_abi = [{
        "stateMutability": "view",
        "type": "function",
        "name": "pricePerShare",
        "inputs": [],
        "outputs": [{"name": "arg_0", "type": "uint256"}]
    }]

    # Contract instance for the provided address and ABI
    yearn_pps = w3.eth.contract(address=yearn_address, abi=pricePerShare_abi)

    # Call the pricePerShare function with the provided block
    pps = yearn_pps.functions.pricePerShare().call(block_identifier=int(block))

    return pps


# Data aggregator Calls
def get_strategy_data(strategy_address, block_number, data_provider_contract=const.DATA_PROVIDER):
    # Convert the data provider address to checksum format
    data_provider_address = Web3.to_checksum_address(data_provider_contract)

    get_strategy_abi = [
        {"inputs": [{"internalType": "address", "name": "_strategy", "type": "address"}], "name": "getStrategy",
         "outputs": [{"components": [{"internalType": "address", "name": "deployedAt", "type": "address"},
                                     {"internalType": "address", "name": "pair", "type": "address"}, {
                                         "components": [{"internalType": "address", "name": "asset", "type": "address"},
                                                        {"internalType": "string", "name": "assetSymbol",
                                                         "type": "string"},
                                                        {"internalType": "uint256", "name": "assetDecimals",
                                                         "type": "uint256"},
                                                        {"internalType": "address", "name": "collateral",
                                                         "type": "address"},
                                                        {"internalType": "string", "name": "collateralSymbol",
                                                         "type": "string"},
                                                        {"internalType": "uint256", "name": "collateralDecimals",
                                                         "type": "uint256"},
                                                        {"internalType": "address", "name": "rateContract",
                                                         "type": "address"},
                                                        {"internalType": "address", "name": "oracle",
                                                         "type": "address"},
                                                        {"internalType": "uint256", "name": "depositLimit",
                                                         "type": "uint256"},
                                                        {"internalType": "uint64", "name": "ratePerSec",
                                                         "type": "uint64"},
                                                        {"internalType": "uint64", "name": "fullUtilizationRate",
                                                         "type": "uint64"},
                                                        {"internalType": "uint32", "name": "feeToProtocolRate",
                                                         "type": "uint32"},
                                                        {"internalType": "uint32", "name": "maxOacleDeviation",
                                                         "type": "uint32"},
                                                        {"internalType": "uint256", "name": "lowExchangeRate",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "highExchangeRate",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "maxLTV",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "protocolLiquidationFee",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "totalAsset",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "totalCollateral",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "totalBorrow",
                                                         "type": "uint256"},
                                                        {"internalType": "uint256", "name": "version",
                                                         "type": "uint256"}],
                                         "internalType": "struct IAggregatorDataProvider.StrategyPairData",
                                         "name": "pairData", "type": "tuple"}],
                      "internalType": "struct IAggregatorDataProvider.StrategyData", "name": "arg_0", "type": "tuple"}],
         "stateMutability": "view", "type": "function"}]

    # Contract instance for the data provider
    data_provider_contract = w3.eth.contract(address=data_provider_address, abi=get_strategy_abi)

    # Call the getStrategy function with the provided strategy address and block number
    strategy_data = data_provider_contract.functions.getStrategy(strategy_address).call(
        block_identifier=int(block_number))

    # Extract relevant data from the returned tuple
    data = {
        'block': int(block_number),
        'collateral': strategy_data[2][3],
        'collateralSymbol': strategy_data[2][4],
        'ratePerSec': strategy_data[2][9],
        'fullUtilizationRate': strategy_data[2][10],
        'lowExchangeRate': strategy_data[2][13] / 1e18,
        'highExchangeRate': strategy_data[2][14] / 1e18,
        'totalAsset': strategy_data[2][17] / 1e18,
        'totalCollateral': strategy_data[2][18] / 1e18,
        'totalBorrow': strategy_data[2][19] / 1e18,
        'newCurrentRateInfo': pair_call_interest(strategy_data[1], int(block_number)),
        'feeToProtocolRate': pair_call_feerate(strategy_data[1], int(block_number))
    }

    return data


def get_strategy_data_for_blocks(strategy_address, block_numbers):
    strategy_data_list = []

    for block_number in block_numbers:
        try:
            strategy_data = get_strategy_data(strategy_address, int(block_number))
            strategy_data_list.append(strategy_data)
        except Exception as e:
            # print(f"Error fetching data for block {block_number}: {e}")
            continue

    return pd.DataFrame(strategy_data_list)


def merge_strategy_data(historic_block_list, strategy_list=const.STRATEGY_LIST, strategy_names=const.STRATEGY_NAME):
    data_list = []

    for i in range(len(strategy_list)):
        strategy_data = get_strategy_data_for_blocks(strategy_list[i], historic_block_list)
        strategy_data = strategy_data.add_suffix(strategy_names[i])
        strategy_data = strategy_data.rename(columns={f'block{strategy_names[i]}': 'block'})
        data_list.append(strategy_data)

    data_list_for_merging = data_list.copy()

    merged_df = data_list_for_merging[0]
    for df in data_list_for_merging[1:]:
        merged_df = pd.merge(merged_df, df, on='block', how='inner')
        merged_df = merged_df.rename(columns={f'block_x': 'block'})

    return merged_df


# Yearn Calls
def fetch_pps(address, block):
    # Convert the address to checksum format
    yearn_address = Web3.to_checksum_address(address)

    # ABI for the pricePerShare function
    pricePerShare_abi = [{
        "stateMutability": "view",
        "type": "function",
        "name": "pricePerShare",
        "inputs": [],
        "outputs": [{"name": "arg_0", "type": "uint256"}]
    }]

    # Contract instance for the provided address and ABI
    yearn_pps = w3.eth.contract(address=yearn_address, abi=pricePerShare_abi)

    # Call the pricePerShare function with the provided block
    pps = yearn_pps.functions.pricePerShare().call(block_identifier=int(block))

    data = {
        'block': int(block),
        'pps': pps
    }

    return data


def get_pps_data_for_blocks(collateral_address, block_numbers):
    pps_data_list = []

    for block_number in block_numbers:
        try:
            pps_data = fetch_pps(collateral_address, int(block_number))
            pps_data_list.append(pps_data)
        except Exception as e:
            continue

    return pd.DataFrame(pps_data_list)


def merge_pps_data(historic_block_list_pps, collateral_list=const.COLLATERAL_LIST, strategy_names=const.STRATEGY_NAME):
    pps_data_list = []

    for i in range(len(collateral_list)):
        pps_data = get_pps_data_for_blocks(collateral_list[i], historic_block_list_pps)
        pps_data = pps_data.add_suffix(strategy_names[i])
        pps_data = pps_data.rename(columns={f'block{strategy_names[i]}': 'block'})
        pps_data_list.append(pps_data)

    pps_data_list_for_merging = pps_data_list.copy()

    merged_pps_df = pps_data_list_for_merging[0]
    for df in pps_data_list_for_merging[1:]:
        merged_pps_df = pd.merge(merged_pps_df, df, on='block', how='inner')
        merged_pps_df = merged_pps_df.rename(columns={f'block_x': 'block'})

    return merged_pps_df


def process_dataframe(df):
    # Create a copy of the DataFrame
    processed_df = df.copy()

    # Number of columns
    num_columns = len(processed_df.columns)

    # Create new columns by shifting existing columns by 180 rows
    for i in range(1, num_columns):
        new_column_name = f'{processed_df.columns[i]}_lagged'
        processed_df[new_column_name] = processed_df.iloc[:, i].shift(180)

    # Divide every column except the first one by 1e18
    for column in processed_df.columns[1:]:
        processed_df[column] /= 1e18

    # Calculate ROI for each column
    for i in range(1, num_columns):
        days = 30
        new_column_name = f'{processed_df.columns[i]}_APY'
        processed_df[new_column_name] = (1 + (
                (processed_df[processed_df.columns[i]] - processed_df[f'{processed_df.columns[i]}_lagged']) /
                processed_df[f'{processed_df.columns[i]}_lagged'])) ** (365.2425 / days) - 1

    # Calculate APR for each column
    for i in range(1, num_columns):
        compounding = 52
        new_column_name = f'{processed_df.columns[i]}_APR'
        processed_df[new_column_name] = compounding * (
                (processed_df[f'{processed_df.columns[i]}_APY'] + 1) ** (1 / compounding)) - compounding

    new_df = pd.DataFrame()
    new_df['block'] = processed_df['block']

    for i in range(1, num_columns):
        new_df[f'{processed_df.columns[i]}'] = processed_df[f'{processed_df.columns[i]}']
        # new_df[f'{processed_df.columns[i]}_APY'] = processed_df[f'{processed_df.columns[i]}_APY']
        new_df[f'{processed_df.columns[i]}_APR'] = processed_df[f'{processed_df.columns[i]}_APR']

    return new_df


def compute_master_data(pps_df, silo_df, strategy_name=const.STRATEGY_NAME):
    # df = pd.DataFrame()

    df = pd.merge(silo_df, pps_df, on='block', how='left')
    df.rename(columns={f'block_x': 'block'}, inplace=True)

    # df.drop(columns=['block_y'], inplace=True)

    output_data = pd.DataFrame()

    output_data['block'] = df['block']

    for i in range(4):
        output_data[f'reserveSize{strategy_name[i]}'] = df[f'totalAsset{strategy_name[i]}']
        output_data[f'currentBorrow{strategy_name[i]}'] = df[f'totalBorrow{strategy_name[i]}']
        output_data[f'utilization{strategy_name[i]}'] = df[f'totalBorrow{strategy_name[i]}'] / df[
            f'totalAsset{strategy_name[i]}']
        output_data[f'collateralApr_{strategy_name[i]}'] = df[f'pps{strategy_name[i]}_APR']
        # borrow_apy = new_current_rate * 31536000 / rate_precision * 100
        output_data[f'borrowApy_{strategy_name[i]}'] = df[f'newCurrentRateInfo{strategy_name[i]}'] * 31536000 / 1e18
        # supply_apy = borrow_apy * (1 - fee_to_protocol_rate / fee_precision ) * utilization_rate / 100
        output_data[f'supplyApy_{strategy_name[i]}'] = output_data[f'borrowApy_{strategy_name[i]}'] * (
                1 - df[f'feeToProtocolRate{strategy_name[i]}'] / 100000) * output_data[
                                                           f'utilization{strategy_name[i]}']
        output_data[f'spread{strategy_name[i]}'] = output_data[f'collateralApr_{strategy_name[i]}'] - output_data[
            f'borrowApy_{strategy_name[i]}']
        output_data[f'oracleLow{strategy_name[i]}'] = df[f'lowExchangeRate{strategy_name[i]}']
        output_data[f'oracleHigh{strategy_name[i]}'] = df[f'highExchangeRate{strategy_name[i]}']
        output_data[f'oracleNormalized{strategy_name[i]}'] = df[f'lowExchangeRate{strategy_name[i]}'] * df[
            f'pps{strategy_name[i]}']

    return output_data


def load_data():
    save_strategy_data = pd.read_csv('E:\Projects\python_projects\pythonProject3\sturdyDataStrategyV1.csv')
    save_pps_data = pd.read_csv('E:\Projects\python_projects\pythonProject3\sturdyDataPpsV1.csv')
    return save_strategy_data, save_pps_data


def get_data_for_blocks(historic_block_list, save_strategy_data, save_pps_data):
    new_strategy_data = merge_strategy_data(historic_block_list=historic_block_list)
    save_strategy_data = save_strategy_data.copy()
    save_strategy_data = pd.concat([save_strategy_data, new_strategy_data], ignore_index=True)

    new_pps_data = merge_pps_data(historic_block_list_pps=historic_block_list)
    save_pps_data = save_pps_data.copy()
    save_pps_data = pd.concat([save_pps_data, new_pps_data], ignore_index=True)

    save_data(save_strategy_data, save_pps_data)

    return save_strategy_data, save_pps_data


def save_data(save_strategy_data, save_pps_data):
    save_strategy_data.to_csv('E:\Projects\python_projects\pythonProject3\sturdyDataStrategyV1.csv', index=False)
    save_pps_data.to_csv('E:\Projects\python_projects\pythonProject3\sturdyDataPpsV1.csv', index=False)
