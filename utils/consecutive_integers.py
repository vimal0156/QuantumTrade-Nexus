"""
Utility for finding consecutive integer groups
"""

from typing import Union, Sequence, Tuple, List, Any
import numpy as np


def find_consecutive_integers(
        idxs: Union[np.ndarray, Sequence[int], Any],
        min_consec: int,
        start_offset: int = 0
) -> List[Tuple[int, int]]:
    """
    Find groups of consecutive integers in an array
    
    Args:
        idxs: Array or sequence of integers
        min_consec: Minimum number of consecutive integers required
        start_offset: Offset to add to the start and end indices
    
    Returns:
        List of tuples containing (start_idx, end_idx) for each group
    """
    # Check to see if the indexes input is empty
    if len(idxs) == 0:
        return []

    # Ensure the indexes are an array, then initialize a list to store the groups
    idxs = np.array(idxs)
    groups = []

    # Find boundaries in consecutive sequences where the difference between
    # consecutive elements is *not* one, then add in the start and ending
    # indexes to the boundaries
    boundaries = np.where(np.diff(idxs) != 1)[0] + 1
    boundaries = np.concatenate(([0], boundaries, [len(idxs)]))

    # Loop over the boundary ranges
    for i in range(0, len(boundaries) - 1):
        # Grab the start and end index of the boundary
        start_idx = boundaries[i]
        end_idx = boundaries[i + 1] - 1

        # Check to see if the length of the group is greater than our minimum threshold
        if end_idx - start_idx + 1 >= min_consec:
            # Update the list of groups
            groups.append((
                int(idxs[start_idx]) + start_offset,
                int(idxs[end_idx]) + start_offset
            ))

    return groups
