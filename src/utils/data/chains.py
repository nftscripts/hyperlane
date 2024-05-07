class Chain:
    def __init__(self, rpc: str, scan: str) -> None:
        self.rpc = rpc
        self.scan = scan


BSC = Chain(
    rpc='https://bsc.blockpi.network/v1/rpc/public',
    scan='https://bscscan.com'
)

NAUTILUS = Chain(
    rpc='https://api.nautilus.nautchain.xyz',
    scan='https://nautscan.com'
)

ETH = Chain(
    rpc='https://rpc.ankr.com/eth',
    scan='https://etherscan.io'
)

BASE = Chain(
    rpc='https://base.blockpi.network/v1/rpc/public',
    scan='https://basescan.org'
)

ARB = Chain(
    rpc='https://arb1.arbitrum.io/rpc',
    scan='https://arbiscan.io'
)

ERA = Chain(
    rpc='https://1rpc.io/zksync2-era',
    scan='https://explorer.zksync.io'
)

SCROLL = Chain(
    rpc='https://rpc.scroll.io',
    scan='https://blockscout.scroll.io'
)

OP = Chain(
    rpc='https://optimism.blockpi.network/v1/rpc/public',
    scan='https://optimistic.etherscan.io'
)

LINEA = Chain(
    rpc='https://linea.blockpi.network/v1/rpc/public',
    scan='https://lineascan.build'
)

chain_mapping = {
    'BSC': BSC,
    'NAUTILUS': NAUTILUS,
    'ETH': ETH,
    'BASE': BASE,
    'ARB': ARB,
    'ERA': ERA,
    'SCROLL': SCROLL,
    'OP': OP,
    'LINEA': LINEA
}
