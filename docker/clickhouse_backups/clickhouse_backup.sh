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
    echo "備份目錄不存在，正在創建: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# 設定時間戳和子目錄名稱
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
SUBFOLDER=$(date +"%Y_%m_%d")

# 創建備份子目錄（如果不存在）
mkdir -p "${BACKUP_DIR}/${SUBFOLDER}"

# 要備份的 Volumes
VOLUMES=(
  "docker_langfuse_clickhouse_data"
  "docker_langfuse_clickhouse_logs"
)

# 備份每個 Volume
for VOLUME in "${VOLUMES[@]}"; do
  BACKUP_FILE="${BACKUP_DIR}/${SUBFOLDER}/${VOLUME}_backup_${TIMESTAMP}.tar.gz"
  
  echo "正在備份 Volume: ${VOLUME} -> ${BACKUP_FILE}"
  
  docker run --rm \
    -v ${VOLUME}:/data \
    -v ${BACKUP_DIR}/${SUBFOLDER}:/backup \
    alpine \
    tar czf /backup/$(basename ${BACKUP_FILE}) -C /data .
  
  echo "備份完成: ${BACKUP_FILE}"
done

echo "所有 Volumes 備份完成，存儲於: ${BACKUP_DIR}/${SUBFOLDER}"
