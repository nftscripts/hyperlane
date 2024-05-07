import random

from abc import (
    abstractmethod,
    ABC,
)

from web3.contract import Contract
from web3.types import TxParams

from src.utils.user.evm.evm_account import EVMAccount
from src.utils.data.chains import chain_mapping
from src.utils.data.tokens import tokens


class ABCBridge(ABC, EVMAccount):
    def __init__(
            self,
            private_key: str,
            contract_address: str,
            abi_name: str,
            amount: float | list[float],
            use_percentage: bool,
            bridge_percentage: float | list[float],
            token: str,
            from_chain: str
    ) -> None:
        rpc = chain_mapping[from_chain.upper()].rpc

        super().__init__(private_key, rpc)
        self.contract_address = contract_address
        self.abi_name = abi_name

        if isinstance(amount, list):
            self.amount = random.uniform(amount[0], amount[1])
        elif isinstance(amount, float):
            self.amount = amount
        else:
            self.logger.error(f'amount must be float or list[float]. Got {type(amount)}')
            return

        self.use_percentage = use_percentage

        if isinstance(bridge_percentage, list):
            self.bridge_percentage = random.uniform(bridge_percentage[0], bridge_percentage[1])
        elif isinstance(bridge_percentage, float):
            self.bridge_percentage = bridge_percentage
        else:
            self.logger.error(f'bridge_percentage must be float or list[float]. Got {type(bridge_percentage)}')
            return

        self.token = token
        self.from_chain = from_chain
        self.scanner = chain_mapping[from_chain.upper()].scan

    async def bridge(self) -> None:
        contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        balance = await self.get_wallet_balance(self.token, tokens[self.from_chain.upper()][self.token.upper()])
        if balance == 0:
            self.logger.error(f'Your wallet balance is 0.. | [{self.wallet_address}]')
            return
        if self.use_percentage:
            amount = int(balance * self.bridge_percentage)
        else:
            amount = await self.create_amount(
                self.token.upper(),
                tokens[self.from_chain.upper()][self.token.upper()],
                self.web3,
                self.amount
            )

        if self.token.upper() != 'ETH' and tokens[self.from_chain.upper()][self.token.upper()] != '...':
            await self.approve_token(
                amount,
                self.private_key,
                tokens[self.from_chain.upper()][self.token.upper()],
                self.contract_address,
                self.wallet_address,
                self.web3
            )

        tx = await self.create_bridge_tx(contract, amount)
        tx_hash = await self.sign_transaction(tx)
        self.logger.debug(f'Successfully sent transaction! | {self.scanner}/tx/{tx_hash}')
        await self.wait_until_tx_finished(tx_hash)

    @abstractmethod
    async def create_bridge_tx(self, contract: Contract, amount: int) -> TxParams:
        """Creates bridge transaction"""
