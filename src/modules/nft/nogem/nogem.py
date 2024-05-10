from typing import Optional
from asyncio import sleep
import random

from web3.contract import Contract
from eth_typing import HexStr

from src.utils.user.evm.evm_account import EVMAccount
from src.utils.data.chains import chain_mapping
from src.utils.wrappers.decorators import retry

from src.utils.data.contracts import (
    contracts,
    abi_names,
)


class Nogem(EVMAccount):
    def __init__(
            self,
            private_key: str,
            action: str,
            mint: Optional[bool],
            from_chain: str | list[str],
            to_chain: str | list[str],
            bridge_all_tokens: Optional[bool],
            percent_to_bridge: Optional[float | list[float]]
    ):
        self.action = action
        self.mint_tokens = mint

        while True:
            if isinstance(from_chain, list):
                self.from_chain = random.choice(from_chain)
            elif isinstance(from_chain, str):
                self.from_chain = from_chain
            else:
                raise ValueError(f'from_chain must be str or list[str]. Got {type(from_chain)}')

            if isinstance(to_chain, list):
                self.to_chain = random.choice(to_chain)
            elif isinstance(to_chain, str):
                self.to_chain = to_chain
            else:
                raise ValueError(f'to_chain must be str or list[str]. Got {type(to_chain)}')

            if self.from_chain == self.to_chain:
                continue
            break

        rpc = chain_mapping[self.from_chain.upper()].rpc
        super().__init__(private_key, rpc)

        self.bridge_all_tokens = bridge_all_tokens

        if isinstance(percent_to_bridge, list):
            self.percent_to_bridge = random.uniform(percent_to_bridge[0], percent_to_bridge[1])
        elif isinstance(percent_to_bridge, float):
            self.percent_to_bridge = percent_to_bridge
        elif percent_to_bridge is None:
            pass
        else:
            raise ValueError(f'percent_to_bridge must be float or list[float]. Got {type(percent_to_bridge)}')

        self.scan = chain_mapping[self.from_chain.upper()].scan
        self.contract_address = contracts['nogem'][action.upper()][self.from_chain.lower()]

        self.domains_mapping = {
            "optimism": 10,
            "celo": 42220,
            "avalanche": 43114,
            "polygon zkevm": 1101,
            "bsc": 56,
            "moonbeam": 1284,
            "gnosis": 100,
            "arbitrum": 42161,
            "polygon": 137,
            "base": 8453,
            "scroll": 534352,
            "eth": 1,
            "manta pacific": 169,
            "mode": 34443,
            "blast": 81457,
            "ancient8": 888888888,
        }

    def __str__(self) -> None:
        return f'{self.__class__.__name__} | {self.from_chain.upper()} => {self.to_chain.upper()} | [{self.wallet_address}]'

    async def run_nft(self) -> None:
        contract = self.load_contract(self.contract_address, self.web3, abi_names['nogem']['nft'])
        tx_hash = await self.mint_nft(contract)
        if tx_hash:
            nft_id = await self.get_nft_id(tx_hash)
            await self.bridge_nft(contract, nft_id)

    async def run_ft(self) -> None:
        contract = self.load_contract(self.contract_address, self.web3, abi_names['nogem']['ft'])

        mint = None
        if self.mint_tokens:
            mint = await self.mint_ft(contract)

        if mint is True or self.mint_tokens is False:
            await self.bridge_ft(contract)

    @retry()
    async def mint_ft(self, contract: Contract) -> bool:
        tokens = random.uniform(0.01, 0.1)
        tx = await contract.functions.mint().build_transaction({
            "chainId": await self.web3.eth.chain_id,
            "from": self.wallet_address,
            "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
            "value": int((tokens / 10000) * 10 ** 18)
        })
        tx_hash = await self.sign_transaction(tx)
        self.logger.debug(f'Mint transaction has been sent | {self.scan}/tx/{tx_hash}')
        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            return True
        return False

    @retry()
    async def bridge_ft(self, contract: Contract) -> None:
        balance = await self.get_wallet_balance('xxx', self.contract_address)
        if balance == 0:
            self.logger.warning(f'Hyperlane FT balance is 0 | [{self.wallet_address}]')
            return

        if self.bridge_all_tokens:
            amount = balance
        else:
            amount = int(balance * self.percent_to_bridge)

        fee = await contract.functions.bridgeFee().call()

        tx = await contract.functions.transferRemote(
            self.domains_mapping[self.to_chain.lower()],
            self.web3.to_bytes(hexstr=('0x' + ('0' * 24) + self.wallet_address.lower()[2:])),
            amount
        ).build_transaction({
            "chainId": await self.web3.eth.chain_id,
            "from": self.wallet_address,
            "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
            "value": fee
        })
        tx_hash = await self.sign_transaction(tx)
        self.logger.debug(f'Bridge transaction has been sent | {self.scan}/tx/{tx_hash}')
        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            self.logger.success(f'Successfully bridged {self.from_chain} => {self.to_chain}')

    @retry()
    async def mint_nft(self, contract: Contract) -> Optional[HexStr]:
        fee = await contract.functions.mintFee().call()
        tx = await contract.functions.mint().build_transaction({
            "chainId": await self.web3.eth.chain_id,
            "from": self.wallet_address,
            "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
            "value": fee
        })
        tx_hash = await self.sign_transaction(tx)
        self.logger.debug(f'Mint transaction has been sent | {self.scan}/tx/{tx_hash}')
        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            return tx_hash

    async def get_nft_id(self, tx_hash: HexStr) -> int:
        while True:
            try:
                receipt = await self.web3.eth.get_transaction_receipt(tx_hash)
                break
            except Exception as ex:
                self.logger.error(ex)
                await sleep(1)

        logs = receipt.get('logs')
        if self.from_chain.upper() == 'POLYGON':
            mint_id_hex = (logs[1]['topics'][3]).hex()
            mint_id = int(mint_id_hex, 16)
        else:
            mint_id_hex = (logs[0]['topics'][3]).hex()
            mint_id = int(mint_id_hex, 16)
        return mint_id

    @retry()
    async def bridge_nft(self, contract: Contract, nft_id: int) -> None:
        fee = await contract.functions.bridgeFee().call()

        tx = await contract.functions.transferRemote(
            self.domains_mapping[self.to_chain.lower()],
            self.web3.to_bytes(hexstr=('0x' + ('0' * 24) + self.wallet_address.lower()[2:])),
            nft_id
        ).build_transaction({
            "chainId": await self.web3.eth.chain_id,
            "from": self.wallet_address,
            "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
            "value": fee
        })
        tx_hash = await self.sign_transaction(tx)
        self.logger.debug(f'Bridge transaction has been sent | {self.scan}/tx/{tx_hash}')
        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            self.logger.success(f'Successfully bridged {self.from_chain} => {self.to_chain}')
