import random

def chance(p: float) -> bool:
    """Returns True with a p% chance.
    """
    return random.random() < p/100

def select(*args: float) -> int:
    """Selects a number 0 to n-1 based on a chance distribution.
    """
    choices = random.choices(range(len(args)), weights=args, k=1)
    return choices[0]

def select_with_remainder(*args: float) -> int:
    """Selects a number 0 to n based on a chance distribution.

    Precondition: 0 <= sum(args) <= 100.
    """
    r = 100 - sum(args)
    if r < 0:
        raise TypeError(f"Remainder must be >= 0, but was {r}")
    l = list(args)
    l.append(r)
    args = tuple(l)
    return select(*args)
