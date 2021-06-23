from eth.vm.forks.berlin.state import (
    BerlinState
)

from .computation import OntherComputation


class OntherState(BerlinState):
    computation_class = OntherComputation
