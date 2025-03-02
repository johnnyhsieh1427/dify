# 修改日期2025-01-23
# 新增欄位，加上OPENDAL_FS_ROOT告知OpenDAL的storage path
from pydantic import Field
from pydantic_settings import BaseSettings


class OpenDALStorageConfig(BaseSettings):
    OPENDAL_SCHEME: str = Field(
        default="fs",
        description="OpenDAL scheme.",
    )
    
    OPENDAL_FS_ROOT: str = Field(
        default="storage",
        description="OpenDAL storage path.",
    )
