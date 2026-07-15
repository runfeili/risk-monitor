from typing import Sequence


class APIKeyManager:
    def __init__(self, keys: Sequence[str]):
        if not keys:
            raise ValueError("At least one API key is required.")

        self._keys = list(keys)
        self._index = 0

    @property
    def current(self) -> str:
        return self._keys[self._index]

    def rotate(self) -> bool:
        self._index += 1

        if self._index >= len(self._keys):
            self._index = 0
            return False

        return True

    @property
    def total(self) -> int:
        return len(self._keys)

    @property
    def current_index(self) -> int:
        return self._index

    def reset(self) -> None:
        self._index = 0
