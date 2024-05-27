import binascii

from web3.contract import Contract
from web3.types import TxParams
import base58

from src.utils.abc.abstract_bridge import ABCBridge
from src.utils.data.contracts import contracts, abi_names


class NautilusBridge(ABCBridge):
    def __init__(
            self,
            private_key: str,
            amount: float | list[float],
            use_percentage: bool,
            bridge_percentage: float | list[float],
            token: str,
            from_chain: str,
            to_chain: str,
            solana_address: str | None = None
    ) -> None:
        contract_address = contracts['nautilus'][from_chain.upper()][token.upper()]
        abi_name = abi_names['nautilus']

        super().__init__(private_key, contract_address, abi_name, amount, use_percentage, bridge_percentage, token,
                         from_chain)

        self.destination_mapping = {
            'NAUTILUS': 22222,
            'BSC': 56,
            'SOLANA': 1399811149
        }
        self.solana_address = solana_address
        self.to_chain = to_chain

    def __str__(self) -> str:
        return f'{self.__class__.__name__} | [{self.token.upper()}] {self.from_chain} => {self.to_chain}'

    async def create_bridge_tx(self, contract: Contract, amount: int) -> TxParams:
        fee = await contract.functions.quoteGasPayment(
            self.destination_mapping[self.to_chain.upper()]
        ).call()

        if self.from_chain.upper() == 'NAUTILUS' and self.token.upper() == 'ZBC':
            value = amount + fee
        else:
            value = fee

        if self.to_chain.upper() != 'SOLANA':
            destination_wallet = self.web3.to_bytes(hexstr=('0x' + ('0' * 24) + self.wallet_address.lower()[2:]))
        else:
            decoded_address = base58.b58decode(self.solana_address)
            hex_address = binascii.hexlify(decoded_address).decode('utf-8')
            destination_wallet = '0x' + hex_address

        tx = await contract.functions.transferRemote(
            self.destination_mapping[self.to_chain.upper()],
            destination_wallet,
            amount
        ).build_transaction({
            "chainId": await self.web3.eth.chain_id,
            "from": self.wallet_address,
            "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
            "value": value
        })

        return tx
