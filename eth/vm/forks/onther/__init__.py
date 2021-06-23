from typing import (
    Type,
)

from eth.rlp.blocks import BaseBlock
from eth.vm.forks.berlin import (
    BerlinVM,
)
from eth.vm.state import BaseState

from .blocks import OntherBlock
from .headers import (
    compute_onther_difficulty,
    configure_onther_header,
    create_onther_header_from_parent,
)
from .state import OntherState


class OntherVM(BerlinVM):
    # fork name
    fork = 'onther'
    print("hi")
    # classes
    block_class: Type[BaseBlock] = OntherBlock
    _state_class: Type[BaseState] = OntherState

    # Methods
    create_header_from_parent = staticmethod(create_onther_header_from_parent)  # type: ignore
    compute_difficulty = staticmethod(compute_onther_difficulty)    # type: ignore
    configure_header = configure_onther_header
