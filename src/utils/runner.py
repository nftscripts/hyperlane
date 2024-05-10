import random

from loguru import logger

from src.modules.bridges.nautilus.nautilus_bridge import NautilusBridge
from src.modules.bridges.merkly.merkly import Merkly
from src.modules.nft.getmint.getmint import GetMint
from src.modules.nft.nogem.nogem import Nogem
from src.modules.nft.zeroway.zeroway import ZeroWay
from src.modules.nft.womex.womex import Womex
from config import *


async def process_nautilus_bridge(private_key: str) -> None:
    from_chain = NautilusBridgeConfig.from_chain
    token = NautilusBridgeConfig.token
    amount = NautilusBridgeConfig.amount
    use_percentage = NautilusBridgeConfig.use_percentage
    bridge_percentage = NautilusBridgeConfig.bridge_percentage

    nautilus_bridge = NautilusBridge(
        private_key=private_key,
        amount=amount,
        use_percentage=use_percentage,
        bridge_percentage=bridge_percentage,
        token=token,
        from_chain=from_chain
    )
    logger.debug(nautilus_bridge)
    await nautilus_bridge.bridge()


async def process_merkly(private_key: str) -> None:
    action = MerklyBridgeConfig.action
    if isinstance(action, list):
        action = random.choice(action)
    elif isinstance(action, str):
        action = action
    else:
        raise ValueError(f'action must be str or list[str]. Got {type(action)}')

    if action.upper() == 'FT':
        mint = MerklyBridgeConfig.mint
        from_chain = MerklyBridgeConfig.from_chain
        to_chain = MerklyBridgeConfig.to_chain
        bridge_all_tokens = MerklyBridgeConfig.bridge_all_tokens
        percent_to_bridge = MerklyBridgeConfig.percent_to_bridge
        amount = None
        use_percentage = None
    elif action.upper() == 'NFT':
        mint = None
        from_chain = MerklyBridgeConfig.from_chain_nft
        to_chain = MerklyBridgeConfig.to_chain_nft
        bridge_all_tokens = None
        percent_to_bridge = None
        amount = None
        use_percentage = None
    elif action.upper() == 'ETH':
        mint = None
        from_chain = MerklyBridgeConfig.from_chain_eth
        to_chain = MerklyBridgeConfig.to_chain_eth
        amount = MerklyBridgeConfig.amount
        use_percentage = MerklyBridgeConfig.use_percentage
        percent_to_bridge = MerklyBridgeConfig.bridge_percentage
        bridge_all_tokens = None
    else:
        raise ValueError(f'Unknown action {action}')

    merkly = Merkly(
        private_key=private_key,
        action=action,
        mint=mint,
        from_chain=from_chain,
        to_chain=to_chain,
        amount=amount,
        bridge_all_tokens=bridge_all_tokens,
        use_percentage=use_percentage,
        percent_to_bridge=percent_to_bridge
    )
    logger.debug(merkly)
    if action.upper() == 'FT':
        await merkly.run_ft()
    elif action.upper() == 'NFT':
        await merkly.run_nft()
    elif action.upper() == 'ETH':
        await merkly.bridge_eth()


async def process_get_mint(private_key: str) -> None:
    from_chain = GetMintConfig.from_chain
    to_chain = GetMintConfig.to_chain
    get_mint = GetMint(
        private_key=private_key,
        from_chain=from_chain,
        to_chain=to_chain
    )
    logger.debug(get_mint)
    await get_mint.run()


async def process_womex(private_key: str) -> None:
    from_chain = WomexConfig.from_chain
    to_chain = WomexConfig.to_chain
    womex = Womex(
        private_key=private_key,
        from_chain=from_chain,
        to_chain=to_chain
    )
    logger.debug(womex)
    await womex.run()


async def process_zeroway(private_key: str) -> None:
    from_chain = ZeroWayConfig.from_chain
    to_chain = ZeroWayConfig.to_chain
    zeroway = ZeroWay(
        private_key=private_key,
        from_chain=from_chain,
        to_chain=to_chain
    )
    logger.debug(zeroway)
    await zeroway.run()


async def process_nogem(private_key: str) -> None:
    action = NogemConfig.action
    if isinstance(action, list):
        action = random.choice(action)
    elif isinstance(action, str):
        action = action
    else:
        raise ValueError(f'action must be str or list[str]. Got {type(action)}')

    if action.upper() == 'FT':
        mint = NogemConfig.mint
        from_chain = NogemConfig.from_chain
        to_chain = NogemConfig.to_chain
        bridge_all_tokens = NogemConfig.bridge_all_tokens
        percent_to_bridge = NogemConfig.percent_to_bridge
    elif action.upper() == 'NFT':
        mint = None
        from_chain = NogemConfig.from_chain_nft
        to_chain = NogemConfig.to_chain_nft
        bridge_all_tokens = None
        percent_to_bridge = None
    else:
        raise ValueError(f'Unknown action {action}')

    nogem = Nogem(
        private_key=private_key,
        action=action,
        mint=mint,
        from_chain=from_chain,
        to_chain=to_chain,
        bridge_all_tokens=bridge_all_tokens,
        percent_to_bridge=percent_to_bridge
    )
    logger.debug(nogem)
    if action.upper() == 'FT':
        await nogem.run_ft()
    elif action.upper() == 'NFT':
        await nogem.run_nft()
