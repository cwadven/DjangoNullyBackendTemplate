from abc import (
    ABC,
    abstractmethod,
)
from typing import Any


class CursorCriteriaInterface(ABC):
    @classmethod
    @abstractmethod
    def is_valid_decoded_cursor(cls, decoded_cursor: dict) -> bool:
        """Define this method to validate decoded cursors in subclasses."""
        pass

    @classmethod
    @abstractmethod
    def get_encoded_base64_cursor_data(cls, data: Any) -> str:
        """Define this method to get cursor data in subclasses."""
        pass

    @classmethod
    @abstractmethod
    def get_ordering_data(cls) -> list[str]:
        pass
