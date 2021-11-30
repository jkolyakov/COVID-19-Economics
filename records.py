"""
Datatypes that are used throughout the program.

At this point I'm assuming that we'll stick to dataclasses, so there isn't really a good reason
for the types to be separate from each other.  Additionally, because they're probably gonna be used
throughout the program, they should probably be in their own file.
"""
import datetime
from dataclasses import dataclass


@dataclass
class StockRecord:
    """TODO
    """
    stock: str
    date: datetime.date
    open: float
    high: float
    low: float
    close: float
    # Open questions:
    # does this way of representing the data make any sense?
    # should these be classes with their own methods instead of just dumb types?


@dataclass
class CovidRecord:
    """TODO
    """
    country: str
    date: datetime.date
    new_cases: int
