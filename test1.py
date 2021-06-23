from eth_keys import keys
from eth_utils import decode_hex, to_wei
from eth_typing import Address

from eth.consensus.pow import mine_pow_nonce
from eth import constants, chains
## Seoul VM is used here
from eth.vm.forks.byzantium import ByzantiumVM
from eth.vm.forks.onther import OntherVM
from eth.db.atomic import AtomicDB


GENESIS_PARAMS = {
    'parent_hash': constants.GENESIS_PARENT_HASH,
    'uncles_hash': constants.EMPTY_UNCLE_HASH,
    'coinbase': constants.ZERO_ADDRESS,
    'transaction_root': constants.BLANK_ROOT_HASH,
    'receipt_root': constants.BLANK_ROOT_HASH,
    'difficulty': 1,
    'block_number': constants.GENESIS_BLOCK_NUMBER,
    'gas_limit': constants.GENESIS_GAS_LIMIT+500000, #why genesis 5000?,
    'timestamp': 1514764800,
    'extra_data': constants.GENESIS_EXTRA_DATA,
    'nonce': constants.GENESIS_NONCE
}

SENDER_PRIVATE_KEY = keys.PrivateKey(
  decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
)

SENDER = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

GENESIS_STATE = {
    SENDER: {
        "balance" : 10**20,
        "nonce" : 0,
        "code" : b"",
        "storage" : {}
    }
}

klass = chains.base.MiningChain.configure(
    __name__='TestChain',
    vm_configuration=(
        (constants.GENESIS_BLOCK_NUMBER, OntherVM),
    )
)

chain = klass.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE)



######### Tx1 ###########################
# nonce = vm.get_transaction_nonce(SENDER)
vm = chain.get_vm()
nonce = vm.state.get_nonce(SENDER)

tx1 = vm.create_unsigned_transaction(
    nonce=nonce,
    gas_price=0,
    gas=100000,
    to=RECEIVER,
    value=0,
    data=b'',
)

signed_tx1 = tx1.as_signed_transaction(SENDER_PRIVATE_KEY)

chain.apply_transaction(signed_tx1)

# We have to finalize the block first in order to be able read the
# attributes that are important for the PoW algorithm
block_result = chain.get_vm().finalize_block(chain.get_block())
block = block_result.block

# based on mining_hash, block number and difficulty we can perform
# the actual Proof of Work (PoW) mechanism to mine the correct
# nonce and mix_hash for this block
nonce, mix_hash = mine_pow_nonce(
    block.number,
    block.header.mining_hash,
    block.header.difficulty
)

block = chain.mine_block(mix_hash=mix_hash, nonce=nonce)

print("BLOCK1 SENDER BALANCE : {}".format(vm.state.get_balance(SENDER)))
print("BLOCK1 RECEIVER BALANCE : {}".format(vm.state.get_balance(RECEIVER)))

######### Tx2 ###########################
# nonce = vm.get_transaction_nonce(SENDER)
vm = chain.get_vm()
nonce = vm.state.get_nonce(SENDER)

tx2 = vm.create_unsigned_transaction(
    nonce=nonce,
    gas_price=0,
    gas=21000,
    to=RECEIVER,
    value=10**18,
    data=b'',
)

signed_tx2 = tx2.as_signed_transaction(SENDER_PRIVATE_KEY)

chain.apply_transaction(signed_tx2)

# We have to finalize the block first in order to be able read the
# attributes that are important for the PoW algorithm
block_result = chain.get_vm().finalize_block(chain.get_block())
block = block_result.block

# based on mining_hash, block number and difficulty we can perform
# the actual Proof of Work (PoW) mechanism to mine the correct
# nonce and mix_hash for this block
nonce, mix_hash = mine_pow_nonce(
    block.number,
    block.header.mining_hash,
    block.header.difficulty
)

block = chain.mine_block(mix_hash=mix_hash, nonce=nonce)
vm = chain.get_vm()

print("tx2.value : {}".format(tx2.value))
print("tx2.txfee : {}".format(tx2.gas * tx2.gas_price))
print("BLOCK2 SENDER BALANCE : {}".format(vm.state.get_balance(SENDER)))
print("BLOCK2 RECEIVER BALANCE : {}".format(vm.state.get_balance(RECEIVER)))
