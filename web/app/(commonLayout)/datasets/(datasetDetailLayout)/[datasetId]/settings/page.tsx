// 修改日期2025-01-13
// 新增Panel套件，導入tracing的功能
import React from 'react'
import { getLocaleOnServer, useTranslation as translate } from '@/i18n/server'
import Form from '@/app/components/datasets/settings/form'
import Panel from '@/app/components/datasets/settings/tracing'

const Settings = async () => {
  const locale = getLocaleOnServer()
  const { t } = await translate(locale, 'dataset-settings')

  return (
    <div className='bg-white h-full overflow-y-auto'>
      <div className='px-6 py-3'>
        <div className='mb-1 text-lg font-semibold text-gray-900'>{t('title')}</div>
        <div className='text-sm text-gray-500'>{t('desc')}</div>
      </div>
      <Panel />
      <Form />
    </div>
  )
}

export default Settings
