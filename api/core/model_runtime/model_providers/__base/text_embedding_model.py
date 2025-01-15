# 修改日期2025-01-14
# 修改class TextEmbeddingModel()的內容
# 修改function invoke()的參數
# 新增dataset和metadata參數

import json
import time
from abc import abstractmethod
from typing import Optional

from pydantic import ConfigDict

from core.entities.embedding_type import EmbeddingInputType
from core.model_runtime.entities.model_entities import ModelPropertyKey, ModelType
from core.model_runtime.entities.text_embedding_entities import TextEmbeddingResult
from core.model_runtime.model_providers.__base.ai_model import AIModel
from core.ops.entities.trace_entity import TraceTaskName
from core.ops.ops_trace_manager import TraceQueueManager, TraceTask
from core.ops.utils import measure_time

# from extensions.ext_database import db
from models.dataset import Dataset


class TextEmbeddingModel(AIModel):
    """
    Model class for text embedding model.
    """

    model_type: ModelType = ModelType.TEXT_EMBEDDING

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())

    def invoke(
        self,
        model: str,
        credentials: dict,
        texts: list[str],
        user: Optional[str] = None,
        input_type: EmbeddingInputType = EmbeddingInputType.DOCUMENT,
        dataset: Optional[Dataset] = None,
        metadata: Optional[dict] = None,
    ) -> TextEmbeddingResult:
        """
        Invoke text embedding model

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :param user: unique user id
        :param input_type: input type
        :return: embeddings result
        """
        is_enable = False
        if dataset:
            trace_config = json.loads(dataset.tracing)
            is_enable = trace_config.get("enabled", False)
            
        self.started_at = time.perf_counter()

        try:
            if is_enable:
                with measure_time() as timer:
                    result = self._invoke(model, credentials, texts, user, input_type)
                trace_manager = TraceQueueManager(app_id=dataset.id, mode="dataset")
                trace_manager.add_trace_task(
                    TraceTask(
                        TraceTaskName.EMBEDDING_TRACE,
                        dataset_id=dataset.id,
                        timer=timer,
                        metadata=metadata,
                        inputs=texts,
                        outputs=result.usage.model_dump_json(),
                        tenant_id=dataset.tenant_id,
                    )
                )
            else:
                result = self._invoke(model, credentials, texts, user, input_type)
            return result
        except Exception as e:
            raise self._transform_invoke_error(e)

    @abstractmethod
    def _invoke(
        self,
        model: str,
        credentials: dict,
        texts: list[str],
        user: Optional[str] = None,
        input_type: EmbeddingInputType = EmbeddingInputType.DOCUMENT,
    ) -> TextEmbeddingResult:
        """
        Invoke text embedding model

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :param user: unique user id
        :param input_type: input type
        :return: embeddings result
        """
        raise NotImplementedError

    @abstractmethod
    def get_num_tokens(self, model: str, credentials: dict, texts: list[str]) -> int:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :return:
        """
        raise NotImplementedError

    def _get_context_size(self, model: str, credentials: dict) -> int:
        """
        Get context size for given embedding model

        :param model: model name
        :param credentials: model credentials
        :return: context size
        """
        model_schema = self.get_model_schema(model, credentials)

        if model_schema and ModelPropertyKey.CONTEXT_SIZE in model_schema.model_properties:
            return model_schema.model_properties[ModelPropertyKey.CONTEXT_SIZE]

        return 1000

    def _get_max_chunks(self, model: str, credentials: dict) -> int:
        """
        Get max chunks for given embedding model

        :param model: model name
        :param credentials: model credentials
        :return: max chunks
        """
        model_schema = self.get_model_schema(model, credentials)

        if model_schema and ModelPropertyKey.MAX_CHUNKS in model_schema.model_properties:
            return model_schema.model_properties[ModelPropertyKey.MAX_CHUNKS]

        return 1
