from eth.vm.forks.petersburg.headers import (
    compute_difficulty,
)
from eth.vm.forks.berlin.headers import (
    configure_header,
    create_header_from_parent,
)


compute_onther_difficulty = compute_difficulty(9000000)

create_onther_header_from_parent = create_header_from_parent(
    compute_onther_difficulty
)
configure_onther_header = configure_header(compute_onther_difficulty)
