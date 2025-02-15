# 修改日期2025-01-13
# 新增作者(created_by)的變數user，用於知道是哪個使用者在操作
from typing import Optional

from core.rag.datasource.keyword.keyword_factory import Keyword
from core.rag.datasource.vdb.vector_factory import Vector
from core.rag.models.document import Document
from models.dataset import Dataset, DocumentSegment


class VectorService:
    @classmethod
    def create_segments_vector(
        cls, keywords_list: Optional[list[list[str]]], segments: list[DocumentSegment], dataset: Dataset, **kwargs
    ):
        user_id = kwargs.get("user_id")
        process_id = kwargs.get("process_id")
        documents = []
        for segment in segments:
            document = Document(
                page_content=segment.content,
                metadata={
                    "doc_id": segment.index_node_id,
                    "doc_hash": segment.index_node_hash,
                    "document_id": segment.document_id,
                    "dataset_id": segment.dataset_id,
                },
            )
            documents.append(document)
        if dataset.indexing_technique == "high_quality":
            # save vector index
            vector = Vector(dataset=dataset)
            vector.add_texts(documents, duplicate_check=True, user_id=user_id, process_id=process_id)

        # save keyword index
        keyword = Keyword(dataset)

        if keywords_list and len(keywords_list) > 0:
            keyword.add_texts(documents, keywords_list=keywords_list)
        else:
            keyword.add_texts(documents)

    @classmethod
    def update_segment_vector(cls, keywords: Optional[list[str]], segment: DocumentSegment, dataset: Dataset, **kwargs):
        # update segment index task
        user_id = kwargs.get("user_id")
        process_id = kwargs.get("process_id")
        # format new index
        document = Document(
            page_content=segment.content,
            metadata={
                "doc_id": segment.index_node_id,
                "doc_hash": segment.index_node_hash,
                "document_id": segment.document_id,
                "dataset_id": segment.dataset_id,
            },
        )
        if dataset.indexing_technique == "high_quality":
            # update vector index
            vector = Vector(dataset=dataset)
            vector.delete_by_ids([segment.index_node_id])
            vector.add_texts([document], duplicate_check=True, user_id=user_id, process_id=process_id)

        # update keyword index
        keyword = Keyword(dataset)
        keyword.delete_by_ids([segment.index_node_id])

        # save keyword index
        if keywords and len(keywords) > 0:
            keyword.add_texts([document], keywords_list=[keywords])
        else:
            keyword.add_texts([document])
