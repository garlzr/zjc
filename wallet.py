import json
from web3 import Web3
from eth_utils import to_checksum_address
from mnemonic import Mnemonic
from eth_account import Account
import concurrent.futures
import threading

# 启用未经审计的HD钱包功能
Account.enable_unaudited_hdwallet_features()

# 定义主流币种的RPC端点
rpc_urls = {
    "Ethereum": "https://mainnet.infura.io/v3/b6bf7d3508c941499b10025c0776eaf8",
    "BSC": "https://bsc-dataseed.binance.org/",
    "Polygon": "https://polygon-mainnet.infura.io/v3/b6bf7d3508c941499b10025c0776eaf8",
    "Avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "Fantom": "https://rpc.ftm.tools/",
    "Optimism": "https://mainnet.optimism.io",
    "Arbitrum": "https://arb1.arbitrum.io/rpc",
}

mnemo = Mnemonic("english")

def get_balance(web3, address):
    balance = web3.eth.get_balance(address)
    return web3.from_wei(balance, 'ether')

def get_tx_count(web3, address):
    return web3.eth.get_transaction_count(address)

def check_balance_and_tx(chain, rpc_url, address, mnemonic):
    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not web3.is_connected():
            print(f"Failed to connect to {chain} RPC at {rpc_url}")
            return

        balance = get_balance(web3, address)
        tx_count = get_tx_count(web3, address)
        result = f"{chain} ---- {address} ---- {balance} ---- {tx_count} ---- {mnemonic}"
        print(result)
        if balance > 0 or tx_count != 0:
            with threading.Lock():
                with open("有余额.txt", "a") as f:
                    f.write(result + "\n")
    except Exception as e:
        print(f"Error checking {chain}: {e}")

def generate_and_check_balance():
    mnemonic = mnemo.generate(strength=128)
    account = Account.from_mnemonic(mnemonic)
    address = account.address

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for chain, rpc_url in rpc_urls.items():
            futures.append(executor.submit(check_balance_and_tx, chain, rpc_url, to_checksum_address(address), mnemonic))
        concurrent.futures.wait(futures)

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _ in range(999999999):
            futures.append(executor.submit(generate_and_check_balance))
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
