# 修改日期2025-01-14
# 修改class TextEmbeddingModel()的內容
# 修改function invoke()的參數
# 新增dataset和metadata參數
# 修改日期2025-01-23
# 修改function invoke()
# 改變偵測enable tracing的方式，先檢查dataset再檢查類型

import json
import logging
import time
from typing import Optional

from pydantic import ConfigDict

from core.entities.embedding_type import EmbeddingInputType
from core.model_runtime.entities.model_entities import ModelPropertyKey, ModelType
from core.model_runtime.entities.text_embedding_entities import TextEmbeddingResult
from core.model_runtime.model_providers.__base.ai_model import AIModel
from core.ops.entities.trace_entity import TraceTaskName
from core.ops.ops_trace_manager import TraceQueueManager, TraceTask
from core.ops.utils import measure_time
from core.plugin.manager.model import PluginModelManager

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
        if dataset and isinstance(dataset.tracing, str):
            try:
                trace_config = json.loads(dataset.tracing)
                is_enable = trace_config.get("enabled", False)
            except Exception as e:
                logging.ERROR(f"Failed to parse tracing config: {e}")
                
        self.started_at = time.perf_counter()

        try:
            plugin_model_manager = PluginModelManager()
            if is_enable:
                with measure_time() as timer:
                    result = plugin_model_manager.invoke_text_embedding(
                        tenant_id=self.tenant_id,
                        user_id=user or "unknown",
                        plugin_id=self.plugin_id,
                        provider=self.provider_name,
                        model=model,
                        credentials=credentials,
                        texts=texts,
                        input_type=input_type.value,
                    )
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
                return plugin_model_manager.invoke_text_embedding(
                    tenant_id=self.tenant_id,
                    user_id=user or "unknown",
                    plugin_id=self.plugin_id,
                    provider=self.provider_name,
                    model=model,
                    credentials=credentials,
                    texts=texts,
                    input_type=input_type.value,
                )
        except Exception as e:
            raise self._transform_invoke_error(e)

    def get_num_tokens(self, model: str, credentials: dict, texts: list[str]) -> list[int]:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :return:
        """
        plugin_model_manager = PluginModelManager()
        return plugin_model_manager.get_text_embedding_num_tokens(
            tenant_id=self.tenant_id,
            user_id="unknown",
            plugin_id=self.plugin_id,
            provider=self.provider_name,
            model=model,
            credentials=credentials,
            texts=texts,
        )

    def _get_context_size(self, model: str, credentials: dict) -> int:
        """
        Get context size for given embedding model

        :param model: model name
        :param credentials: model credentials
        :return: context size
        """
        model_schema = self.get_model_schema(model, credentials)

        if model_schema and ModelPropertyKey.CONTEXT_SIZE in model_schema.model_properties:
            content_size: int = model_schema.model_properties[ModelPropertyKey.CONTEXT_SIZE]
            return content_size

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
            max_chunks: int = model_schema.model_properties[ModelPropertyKey.MAX_CHUNKS]
            return max_chunks

        return 1
