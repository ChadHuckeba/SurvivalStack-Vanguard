from abc import ABC
from .engine import SQLiteEngine

class BaseDAO(ABC):
    """
    Abstract base class for Data Access Objects.
    Provides common access to the SQLite engine.
    """
    def __init__(self, engine: SQLiteEngine) -> None:
        self.engine = engine
