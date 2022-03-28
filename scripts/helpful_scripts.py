from brownie import accounts, network, config
import eth_utils

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local", "hardhat"]


def upgrade(
    account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,
    initialiser=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initialiser:
            encoded_function_call = encode_function_data(initialiser, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, new_implementation_address, {"from": account}
            )
    else:
        if initialiser:
            encoded_function_call = encode_function_data(initialiser, *args)
            transaction = proxy.upgradeToAndCall(
                new_implementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy.upgradeTo(new_implementation_address, {"from": account})
    return transaction


def encode_function_data(initialiser=None, *args):
    # encodes the function call so we can work with an initialiser
    if len(args) == 0 or not initialiser:
        return eth_utils.to_bytes(hexstr="0x")  # empty hexstring if no arguments given
    return initialiser.encode_input(*args)  # returns the encoded bytes


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None
