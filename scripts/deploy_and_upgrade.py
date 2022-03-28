from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    BoxV2,
    network,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)


def main():
    # implementation contract
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)

    # hooking up a proxy to implementation contract
    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    # encoding the initialiser function into bytes
    initialiser = box.store, 1
    box_encoded_initaliser_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,  # implementation contract address
        proxy_admin.address,  # admin address
        box_encoded_initaliser_function,  # function selector
        {"from": account, "gas_limit": 1_000_000},
        publish_source=True,
    )
    print(f"Proxy deployed to {proxy}. You can now upgrade to V2.")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    # print(proxy_box.retrieve())

    # upgrading
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded.")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
