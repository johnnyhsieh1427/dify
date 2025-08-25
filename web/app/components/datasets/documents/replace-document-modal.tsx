// 修改日期2025-08-25
// 增加新的功能元件，將替換檔案的功能獨立出來
import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Modal from '@/app/components/base/modal'
import Button from '@/app/components/base/button'

type ReplaceDocumentModalProps = {
    isShow: boolean
    onClose: () => void
    onReplace: (fileItem: File) => void
}

const ReplaceDocumentModal = ({ isShow, onClose, onReplace }: ReplaceDocumentModalProps) => {
  const { t } = useTranslation()
  const [fileItem, setFileItem] = useState<File | null>(null)
  return (
    <Modal isShow={isShow} onClose={onClose} title="替換文件">
      <div>
        <input type="file" onChange={e => setFileItem(e.target.files?.[0] || null)} />
      </div>
      <div className="mt-4 flex justify-end">
        <Button onClick={onClose}>{t('datasetDocuments.list.batchModal.cancel')}</Button>
        <Button
          disabled={!fileItem}
          onClick={() => fileItem && onReplace(fileItem)}
        >{t('datasetDocuments.list.batchModal.ok')}</Button>
      </div>
    </Modal>
  )
}
export default ReplaceDocumentModal
