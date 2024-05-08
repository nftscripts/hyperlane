from abc import abstractmethod, ABC

from eth_typing import HexStr
from web3.contract import Contract
from web3.types import TxParams

from src.utils.data.chains import chain_mapping
from src.utils.data.contracts import abi_names
from src.utils.user.evm.evm_account import EVMAccount
from src.utils.wrappers.decorators import retry


class ABCMintBridge(ABC, EVMAccount):
    def __init__(
            self,
            private_key: str,
            from_chain: str,
            to_chain: str,
            contract_address: str,
            name: str
    ):
        self.from_chain = from_chain
        self.to_chain = to_chain
        rpc = chain_mapping[self.from_chain.upper()].rpc
        self.scan = chain_mapping[self.from_chain.upper()].scan
        super().__init__(private_key, rpc)
        self.contract_address = contract_address
        self.name = name

        self.domains_mapping = {
            "optimism": 10,
            "celo": 42220,
            "avalanche": 43114,
            "polygon zkevm": 1101,
            "bsc": 56,
            "moonbeam": 1284,
            "gnosis": 100,
            "arb": 42161,
            "polygon": 137,
            "base": 8453,
            "scroll": 534352,
            "eth": 1,
            "manta pacific": 169,
            "mode": 34443,
            "blast": 81457,
            "ancient8": 888888888,
        }

    @abstractmethod
    async def create_mint_transaction(self, contract: Contract) -> TxParams:
        """Creates mint transaction"""

    @abstractmethod
    async def create_bridge_transaction(self, contract: Contract, nft_id: int) -> TxParams:
        """Creates bridge transaction"""

    @abstractmethod
    async def get_nft_id(self, tx_hash: HexStr) -> int:
        """Returns nft id"""

    @retry()
    async def mint_nft(self, contract: Contract) -> None:
        mint_tx = await self.create_mint_transaction(contract)
        tx_hash = await self.sign_transaction(mint_tx)
        self.logger.debug(f'Mint transaction has been sent | {self.scan}/tx/{tx_hash}')
        confirmed = await self.wait_until_tx_finished(tx_hash)

        if confirmed:
            return tx_hash

    @retry()
    async def bridge_nft(self, contract: Contract, nft_id: int) -> None:
        bridge_tx = await self.create_bridge_transaction(contract, nft_id)
        tx_hash = await self.sign_transaction(bridge_tx)
        self.logger.debug(f'Bridge transaction has been sent | {self.scan}/tx/{tx_hash}')
        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            self.logger.success(f'Successfully bridged {self.from_chain} => {self.to_chain}')

    async def run(self) -> None:
        contract = self.load_contract(self.contract_address, self.web3, abi_names[self.name])
        mint_hash = await self.mint_nft(contract)
        if mint_hash:
            nft_id = await self.get_nft_id(mint_hash)
            await self.bridge_nft(contract, nft_id)
