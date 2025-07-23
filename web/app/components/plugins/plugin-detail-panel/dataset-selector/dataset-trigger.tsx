'use client'
import React from 'react'
import { useTranslation } from 'react-i18next'
import {
  RiArrowDownSLine,
} from '@remixicon/react'
import { Folder } from '@/app/components/base/icons/src/vender/solid/files'
import type { DataSet } from '@/models/datasets'
import cn from '@/utils/classnames'

type Props = {
  open: boolean
  datasetDetail?: DataSet[]
}

const DatasetTrigger = ({
  open,
  datasetDetail,
}: Props) => {
  const { t } = useTranslation()
  return (
    <div className={cn(
      'group flex cursor-pointer items-center rounded-lg bg-components-input-bg-normal p-2 pl-3 hover:bg-state-base-hover-alt',
      open && 'bg-state-base-hover-alt',
      datasetDetail && 'py-1.5 pl-1.5',
    )}>
      {datasetDetail && datasetDetail.length > 0 && (
        <Folder className='h-5 w-5 text-[#444CE7]' />
      )}
      {datasetDetail && datasetDetail.length > 0 && (
        <div title={datasetDetail[0].name} className='system-sm-medium grow text-components-input-text-filled'>{datasetDetail[0].name}</div>
      )}
      {(!datasetDetail || datasetDetail.length === 0) && (
        <div className='system-sm-regular grow truncate text-components-input-text-placeholder'>{t('app.appSelector.placeholder')}</div>
      )}
      {datasetDetail && datasetDetail.length > 1 && (
        <div className='system-xs-medium flex h-7 cursor-pointer items-center rounded-lg bg-components-panel-bg px-2 text-text-tertiary'>
          {`+ ${datasetDetail.length - 1}`}
        </div>
      )}
      <RiArrowDownSLine className={cn('ml-0.5 h-4 w-4 shrink-0 text-text-quaternary group-hover:text-text-secondary', open && 'text-text-secondary')} />
    </div>
  )
}

export default DatasetTrigger
