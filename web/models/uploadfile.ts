// 修改日期2025-07-23
// 新增UploadFiles的欄位資料型態

export type UploadFiles = {
  id: string
  tenant_id: string
  storage_type: string
  key: string
  name: string
  size: number
  extension: string
  mime_type: string | null
  created_by: string
  created_at: string
  used: boolean
  used_by: string | null
  used_at: string | null
  hash: string | null
  created_by_role: string
  source_url: string
}
