#!/bin/bash

# 檢查是否有輸入備份目錄參數
if [ $# -ge 1 ]; then
    BACKUP_DIR=$1
else
    BACKUP_DIR="$(pwd)/backup_dir"
    echo "未指定備份目錄，將使用當前目錄下的 backup_dir 作為備份位置: $BACKUP_DIR"
fi

# 檢查備份目錄是否存在
if [ ! -d "$BACKUP_DIR" ]; then
    echo "錯誤: 指定的備份目錄不存在: $BACKUP_DIR"
    exit 1
fi

# 顯示可用的備份檔案
echo "以下是可用的備份檔案:"
find "$BACKUP_DIR" -type f -name "*_backup_*.tar.gz" -print

# 提示使用者選擇備份檔案
read -p "請輸入要還原的備份檔案完整路徑: " BACKUP_FILE

# 檢查選擇的備份檔案是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo "錯誤: 指定的備份檔案不存在: $BACKUP_FILE"
    exit 1
fi

# 提取 Volume 名稱
VOLUME_NAME=$(basename "$BACKUP_FILE" | cut -d'_' -f1-3)

# 還原備份到對應的 Volume
echo "正在還原備份檔案: $BACKUP_FILE 到 Volume: $VOLUME_NAME"

docker run --rm \
    -v ${VOLUME_NAME}:/data \
    -v $(dirname "$BACKUP_FILE"):/backup \
    alpine \
    tar xzf /backup/$(basename "$BACKUP_FILE") -C /data

if [ $? -eq 0 ]; then
    echo "還原完成: $VOLUME_NAME"
else
    echo "還原失敗: $VOLUME_NAME"
    exit 1
fi
