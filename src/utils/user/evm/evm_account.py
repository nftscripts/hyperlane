from asyncio import sleep
from time import time

from web3.exceptions import TransactionNotFound
from web3.types import TxParams
from hexbytes import HexBytes
from web3.eth import AsyncEth
from eth_typing import HexStr
from web3 import AsyncWeb3

from src.utils.user.evm.utils import Utils


class EVMAccount(Utils):
    def __init__(self, private_key: str, rpc: str) -> None:
        self.private_key = private_key

        self.web3 = AsyncWeb3(
            provider=AsyncWeb3.AsyncHTTPProvider(
                endpoint_uri=rpc,
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[]
        )
        self.account = self.web3.eth.account.from_key(private_key)
        self.wallet_address = self.account.address

        super().__init__()

    async def get_wallet_balance(self, token: str = 'ETH', stable_address: str = None) -> float:
        if token.lower() != 'eth' and stable_address != '...':
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(stable_address),
                                              abi=self.load_abi('erc20'))
            balance = await contract.functions.balanceOf(self.wallet_address).call()
        else:
            balance = await self.web3.eth.get_balance(self.wallet_address)

        return balance

    async def sign_transaction(self, tx: TxParams) -> HexBytes:
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        return tx_hash

    async def wait_until_tx_finished(self, tx_hash: HexStr, max_wait_time=180) -> bool:
        start_time = time()
        while True:
            try:
                receipts = await self.web3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    self.logger.success(f"Transaction confirmed!")
                    return True
                elif status is None:
                    await sleep(0.3)
                else:
                    self.logger.error(f"Transaction failed!")
                    return False
            except TransactionNotFound:
                if time() - start_time > max_wait_time:
                    print(f'FAILED TX: {hash}')
                    return False
                await sleep(1)
