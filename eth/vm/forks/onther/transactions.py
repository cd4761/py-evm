from eth_keys.datatypes import PrivateKey
from eth_typing import Address

from eth.vm.forks.berlin.transactions import (
    BerlinLegacyTransaction,
    BerlinUnsignedLegacyTransaction,
)

from eth._utils.transactions import (
    create_transaction_signature,
)


class OntherTransaction(BerlinLegacyTransaction):
    @classmethod
    def create_unsigned_transaction(cls,
                                    *,
                                    nonce: int,
                                    gas_price: int,
                                    gas: int,
                                    to: Address,
                                    value: int,
                                    data: bytes) -> 'OntherUnsignedTransaction':
        return OntherUnsignedTransaction(nonce, gas_price, gas, to, value, data)


class OntherUnsignedTransaction(BerlinUnsignedLegacyTransaction):
    def as_signed_transaction(self,
                              private_key: PrivateKey,
                              chain_id: int = None) -> OntherTransaction:
        v, r, s = create_transaction_signature(self, private_key, chain_id=chain_id)
        return OntherTransaction(
            nonce=self.nonce,
            gas_price=self.gas_price,
            gas=self.gas,
            to=self.to,
            value=self.value,
            data=self.data,
            v=v,
            r=r,
            s=s,
        )
