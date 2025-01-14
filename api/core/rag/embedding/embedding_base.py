# 修改日期2025-01-13
# 修改function embed_documents()的參數
# 新增metadata、dataset和**kwargs參數
from abc import ABC, abstractmethod
from models.dataset import Dataset
from typing import Any, Optional

class Embeddings(ABC):
    """Interface for embedding models."""

    @abstractmethod
    def embed_documents(
        self, 
        texts: list[str], 
        dataset: Optional[Dataset] = None, 
        metadata: Optional[dict[str, Any]] = None, 
        **kwargs: Any
    ) -> list[list[float]]:
        """Embed search docs."""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        raise NotImplementedError

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous Embed search docs."""
        raise NotImplementedError

    async def aembed_query(self, text: str) -> list[float]:
        """Asynchronous Embed query text."""
        raise NotImplementedError
