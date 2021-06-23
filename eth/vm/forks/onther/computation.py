from eth.vm.forks.berlin.computation import (
    BERLIN_PRECOMPILES
)
from eth.vm.forks.berlin.computation import (
    BerlinComputation,
)

from .opcodes import ONTHER_OPCODES

ONTHER_PRECOMPILES = BERLIN_PRECOMPILES


class OntherComputation(BerlinComputation):
    """
    A class for all execution computations in the ``Onther`` fork.
    Inherits from :class:`~eth.vm.forks.constantinople.berlin.BerlinComputation`
    """
    # Override
    opcodes = ONTHER_OPCODES
    _precompiles = ONTHER_PRECOMPILES
