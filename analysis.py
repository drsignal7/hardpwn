from typing import List, Optional

COMMON_BAUDS = [115200, 57600, 38400, 19200, 9600]

def estimate_baud_from_edges(edges: List[float]) -> Optional[int]:
    if not edges:
        return None
    try:
        median = sorted(edges)[len(edges)//2]
        if median <= 0:
            return None
        # edges are microseconds per bit (approx). Convert to baud
        baud_est = int(round(1_000_000 / median))
        # choose nearest common baud
        snap = min(COMMON_BAUDS, key=lambda b: abs(b - baud_est))
        if abs(snap - baud_est) / snap < 0.4:
            return snap
    except Exception:
        return None
    return None

def confidence_from_count(n:int, max_n:int=4)->float:
    return min(0.95, 0.4 + 0.15 * min(n, max_n))
