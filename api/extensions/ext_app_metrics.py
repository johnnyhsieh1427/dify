# 修改日期2025-01-13
# 新增API端點，用於查看文件上傳的檔案function upload_files()
import json
import mimetypes
import os
import threading

from flask import Response, send_file

from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    @app.after_request
    def after_request(response):
        """Add Version headers to the response."""
        response.headers.add("X-Version", dify_config.CURRENT_VERSION)
        response.headers.add("X-Env", dify_config.DEPLOY_ENV)
        return response

    @app.route("/health")
    def health():
        return Response(
            json.dumps({"pid": os.getpid(), "status": "ok", "version": dify_config.CURRENT_VERSION}),
            status=200,
            content_type="application/json",
        )

    @app.route("/threads")
    def threads():
        num_threads = threading.active_count()
        threads = threading.enumerate()

        thread_list = []
        for thread in threads:
            thread_name = thread.name
            thread_id = thread.ident
            is_alive = thread.is_alive()

            thread_list.append(
                {
                    "name": thread_name,
                    "id": thread_id,
                    "is_alive": is_alive,
                }
            )

        return {
            "pid": os.getpid(),
            "thread_num": num_threads,
            "threads": thread_list,
        }

    @app.route("/db-pool-stat")
    def pool_stat():
        from extensions.ext_database import db

        engine = db.engine
        return {
            "pid": os.getpid(),
            "pool_size": engine.pool.size(),
            "checked_in_connections": engine.pool.checkedin(),
            "checked_out_connections": engine.pool.checkedout(),
            "overflow_connections": engine.pool.overflow(),
            "connection_timeout": engine.pool.timeout(),
            "recycle_time": db.engine.pool._recycle,
        }
        
    @app.route("/upload_files/<folder_name>/<file_name>")
    def upload_files(folder_name: str, file_name: str):
        try:
            # 確保檔案存在
            storage_type = dify_config.STORAGE_TYPE
            if storage_type == "local":
                root_path = dify_config.STORAGE_LOCAL_PATH
            elif storage_type == "opendal":
                root_path = dify_config.OPENDAL_FS_ROOT
            else:
                raise ValueError(f"Unsupport storage type: {storage_type}")
            
            file_path = os.path.join(
                root_path,
                "upload_files",
                folder_name, 
                file_name
            )

            if not os.path.exists(file_path):
                return Response("File not found", status=404)

            # 自動偵測檔案的 MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            # 設置回應，Content-Disposition 為 inline（直接顯示）
            response = send_file(file_path, mimetype=mime_type)
            response.headers["Content-Disposition"] = f"inline; filename={file_name}"
            return response

        except FileNotFoundError:
            return Response(
                json.dumps({"error": "file not found"}),
                status=404,
                content_type="application/json",
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                content_type="application/json",
            )
            