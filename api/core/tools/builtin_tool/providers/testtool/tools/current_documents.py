import json
from collections.abc import Generator
from typing import Any, Optional

from configs import dify_config
from core.tools.builtin_tool.tool import BuiltinTool
from core.tools.entities.tool_entities import ToolInvokeMessage


class CurrentDocumentsTool(BuiltinTool):
    def _invoke(
        self,
        user_id: str,
        tool_parameters: dict[str, Any],
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        datasets = tool_parameters.get("dataset_id", "")
        try:
            import ast
            datasets = ast.literal_eval(datasets)
            tmp = []
            for dataset in datasets:
                tmp_data = {
                    "id": dataset.get("id", ""),
                    "name": dataset.get("name", ""),
                    "documents": [
                        {
                            "document_name": doc.get("name", ""),
                            "download_url": f"{dify_config.CONSOLE_API_URL.rstrip('/')}/{doc.get('key', '')}"
                        } for doc in dataset.get("documents", [])
                    ],
                }
                tmp.append(tmp_data)
        except Exception as e:
            yield self.create_text_message(json.dumps({"error": str(e)}, indent=2))
            return
        yield self.create_text_message(json.dumps({"dataset_docs": tmp}, indent=2))
        yield self.create_json_message({"dataset_docs": tmp})
