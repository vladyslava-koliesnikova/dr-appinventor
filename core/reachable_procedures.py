from collections import deque
from typing import Set, Dict

def compute_reachable_procedures(
    call_graph: Dict[str, Set[str]],
    entry_procedures: Set[str],
    all_defined: Set[str],
) -> Set[str]:
    """BFS from event‑called procedures through the call graph."""
    reachable = set()
    queue = deque(entry_procedures)

    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        for callee in call_graph.get(current, set()):
            if callee not in reachable and callee in all_defined:
                queue.append(callee)
    return reachable