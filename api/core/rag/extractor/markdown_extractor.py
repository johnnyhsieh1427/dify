# 修改日期2025-08-25
# 增加markdown內嵌圖片上傳到server功能，轉換成網址顯示
"""Abstract interface for document loader implementations."""

import base64
import binascii
import datetime
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Optional

from configs import dify_config
from core.rag.extractor.extractor_base import BaseExtractor
from core.rag.extractor.helpers import detect_file_encodings
from core.rag.models.document import Document
from extensions.ext_database import db
from extensions.ext_storage import storage
from models.enums import CreatorUserRole
from models.model import UploadFile


class MarkdownExtractor(BaseExtractor):
    """Load Markdown files.


    Args:
        file_path: Path to the file to load.
    """

    def __init__(
        self,
        file_path: str,
        tenant_id: str,
        user_id: str,
        remove_hyperlinks: bool = False,
        remove_images: bool = False,
        encoding: Optional[str] = None,
        autodetect_encoding: bool = True,
    ):
        """Initialize with file path."""
        self._file_path = file_path
        self.tenant_id = tenant_id
        self.user_id = user_id
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        self._encoding = encoding
        self._autodetect_encoding = autodetect_encoding

    def extract(self) -> list[Document]:
        """Load from file path."""
        tups = self.parse_tups(self._file_path)
        documents = []
        for header, value in tups:
            value = value.strip()
            if header is None:
                documents.append(Document(page_content=value))
            else:
                documents.append(Document(page_content=f"\n\n{header}\n{value}"))

        return documents

    def markdown_to_tups(self, markdown_text: str) -> list[tuple[Optional[str], str]]:
        """Convert a markdown file to a dictionary.

        The keys are the headers and the values are the text under each header.

        """
        markdown_tups: list[tuple[Optional[str], str]] = []
        lines = markdown_text.split("\n")

        current_header = None
        current_text = ""
        code_block_flag = False

        for line in lines:
            if line.startswith("```"):
                code_block_flag = not code_block_flag
                current_text += line + "\n"
                continue
            if code_block_flag:
                current_text += line + "\n"
                continue
            header_match = re.match(r"^#+\s", line)
            if header_match:
                markdown_tups.append((current_header, current_text))
                current_header = line
                current_text = ""
            else:
                current_text += line + "\n"
        markdown_tups.append((current_header, current_text))

        markdown_tups = [
            (re.sub(r"#", "", key).strip() if key else None, re.sub(r"<.*?>", "", value))
            for key, value in markdown_tups
        ]

        return markdown_tups

    def remove_images(self, content: str) -> str:
        """Get a dictionary of a markdown file from its path."""
        pattern = r"!{1}\[\[(.*)\]\]"
        content = re.sub(pattern, "", content)
        return content

    def _extract_images_from_markdown(self, md_text: str):
        """Extract images from a markdown document."""
        pattern = re.compile(
            r"!\[(?P<alt>[^\]]*)\]\("
            r"\s*data:(?P<mime>image)/"
            r"(?P<subtype>[a-z0-9.+-]+);base64,"
            r"(?P<data>[A-Za-z0-9+/=\r\n]+)\)",
            re.IGNORECASE | re.VERBOSE | re.DOTALL,
        )
        def _replace_one(m: re.Match) -> str:

            subtype_raw = m.group("subtype").lower()
            b64_data = (m.group("data") or "").replace("\n", "").replace("\r", "")

            # 推導副檔名：svg+xml → svg；heic、avif 等照樣保留
            # 這裡優先以 '+' 切，再以 '_' 切，確保 svg+xml 這類能得到 'svg'
            ext = subtype_raw.split("+", 1)[0].split("_", 1)[0]
            if ext == "svg" and "xml" in subtype_raw:
                ext = "svg"  # 明確處理 svg+xml

            try:
                img_bytes = base64.b64decode(b64_data, validate=True)
            except binascii.Error:
                # base64 壞掉就不動原文
                return m.group(0)

            # 產生檔名與儲存路徑
            file_uuid = str(uuid.uuid4())
            file_key = f"image_files/{self.tenant_id}/{file_uuid}.{ext}"

            # 推測 MIME
            mime_type, _ = mimetypes.guess_type(file_key)
            if not mime_type:
                # 從 subtype 猜
                mime_type = f"image/{subtype_raw}"

            storage.save(file_key, img_bytes)

            # 建立 DB 紀錄
            now_utc_naive = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
            upload_file = UploadFile(
                tenant_id=self.tenant_id,
                storage_type=dify_config.STORAGE_TYPE,
                key=file_key,
                name=file_key,
                size=len(img_bytes),
                extension=str(ext),
                mime_type=mime_type or "",
                created_by=self.user_id,
                created_by_role=CreatorUserRole.ACCOUNT,
                created_at=now_utc_naive,
                used=True,
                used_by=self.user_id,
                used_at=now_utc_naive,
            )
            db.session.add(upload_file)
            db.session.commit()

            # 產生可預覽/下載的 URL（照你原本的邏輯）
            file_url = f"{dify_config.FILES_URL}/files/{upload_file.id}/file-preview"
            return f"![image]({file_url})"

        # 做整體替換
        new_markdown = pattern.sub(_replace_one, md_text)
        return new_markdown

    def remove_hyperlinks(self, content: str) -> str:
        """Get a dictionary of a markdown file from its path."""
        pattern = r"\[(.*?)\]\((.*?)\)"
        content = re.sub(pattern, r"\1", content)
        return content

    def parse_tups(self, filepath: str) -> list[tuple[Optional[str], str]]:
        """Parse file into tuples."""
        content = ""
        try:
            content = Path(filepath).read_text(encoding=self._encoding)
        except UnicodeDecodeError as e:
            if self._autodetect_encoding:
                detected_encodings = detect_file_encodings(filepath)
                for encoding in detected_encodings:
                    try:
                        content = Path(filepath).read_text(encoding=encoding.encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {filepath}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {filepath}") from e

        if self._remove_hyperlinks:
            content = self.remove_hyperlinks(content)

        if self._remove_images:
            content = self.remove_images(content)
        else:
            content = self._extract_images_from_markdown(content)

        # return self.markdown_to_tups(content)
        return [(None, content)]
