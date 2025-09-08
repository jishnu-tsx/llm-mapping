from abc import ABC, abstractmethod
from typing import List, Optional


class BaseProvider(ABC):
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def generate(
        self, prompt: str, images: Optional[List[str]] = None
    ) -> Optional[str]:
        """Generate content from prompt + images."""
        pass
