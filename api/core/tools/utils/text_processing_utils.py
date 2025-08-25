# 修改日期2025-08-25
# 修改內容: 將markdown的語法在開頭中保留
import re


def remove_leading_symbols(text: str) -> str:
    """
    Remove leading punctuation or symbols from the given text.

    Args:
        text (str): The input text to process.

    Returns:
        str: The text with leading punctuation or symbols removed.
    """
    # Match Unicode ranges for punctuation and symbols
    # FIXME this pattern is confused quick fix for #11868 maybe refactor it later
    # pattern = r"^[\u2000-\u206F\u2E00-\u2E7F\u3000-\u303F!\"#$%&'()*+,./:;<=>?@^_`~]+"
    """
    去除開頭的標點／符號，但不破壞 Markdown/HTML：
    - 不移除以 `<tag...>`（含 HTML、autolink `<http://...>`、`<!—…—>`）開頭
    - 不移除以 `![alt](url)` 的圖片語法開頭
    """
    # 只有當「不是」(<字母/!/ /) 或 (Markdown 圖片 `![`) 開頭時，才允許剔除前導符號
    pattern = (
        r"^(?!"                # 開頭不是以下情形：
        r"(?:<\s*[A-Za-z!/])"  # 1) <tag…> / <!…> / </…> / <http…> 等 HTML/自動連結
        r"|(?:!\[)"            # 2) Markdown 圖片語法 ![alt](url)
        r")"
        r"[\u2000-\u206F\u2E00-\u2E7F\u3000-\u303F!\"#$%&'()*+,./:;<=>?@^_`~]+"
    )
    return re.sub(pattern, "", text)
