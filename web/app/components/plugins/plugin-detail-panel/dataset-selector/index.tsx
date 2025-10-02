'use client'
import type { FC } from 'react'
import React, { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  PortalToFollowElem,
  PortalToFollowElemContent,
  PortalToFollowElemTrigger,
} from '@/app/components/base/portal-to-follow-elem'
import DatasetTrigger from '@/app/components/plugins/plugin-detail-panel/dataset-selector/dataset-trigger'
import DatasetPicker from '@/app/components/plugins/plugin-detail-panel/dataset-selector/dataset-picker'
import type {
  OffsetOptions,
  Placement,
} from '@floating-ui/react'
import useSWRInfinite from 'swr/infinite'
import { fetchDatasets } from '@/service/datasets'
import type { DataSet, DataSetListResponse } from '@/models/datasets'
import type { UploadFiles } from '@/models/uploadfile'

const PAGE_SIZE = 20

const getKey = (
  pageIndex: number,
  previousPageData: DataSetListResponse,
  searchText: string,
) => {
  if (pageIndex === 0 || (previousPageData && previousPageData.has_more)) {
    const params: any = {
      url: 'datasets',
      params: {
        page: pageIndex + 1,
        limit: PAGE_SIZE,
        name: searchText,
      },
    }
    return params
  }
  return null
}

type Props = {
  value?: (DataSet & { documents: UploadFiles[] })[]
  scope?: string
  disabled?: boolean
  placement?: Placement
  offset?: OffsetOptions
  onSelect: (selectedDatasets: (DataSet & { documents: UploadFiles[] })[]) => void
  supportAddCustomTool?: boolean
}

const DatasetSelector: FC<Props> = ({
  value,
  scope,
  disabled,
  placement = 'bottom',
  offset = 4,
  onSelect,
}) => {
  const { t } = useTranslation()
  const [isShow, onShowChange] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const { data, isLoading, setSize } = useSWRInfinite(
    (pageIndex: number, previousPageData: DataSetListResponse) => getKey(pageIndex, previousPageData, searchText),
    fetchDatasets,
    {
      revalidateFirstPage: true,
      shouldRetryOnError: false,
      dedupingInterval: 500,
      errorRetryCount: 3,
    },
  )

  const displayedDatasets = useMemo(() => {
    if (!data) return []
    return data.flatMap(({ data: datasets }) => datasets)
  }, [data])

  const hasMore = data?.at(-1)?.has_more ?? true

  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore) return

    setIsLoadingMore(true)
    try {
      await setSize((size: number) => size + 1)
    }
    finally {
      // Add a small delay to ensure state updates are complete
      setTimeout(() => {
        setIsLoadingMore(false)
      }, 300)
    }
  }, [isLoadingMore, hasMore, setSize])

  const handleTriggerClick = () => {
    if (disabled) return
    onShowChange(true)
  }

  const [isShowChooseDataset, setIsShowChooseDataset] = useState(false)

  const handleSelectDataset = (selectedDatasets: (DataSet & { documents: UploadFiles[] })[]) => {
    onSelect(selectedDatasets)
    // setIsShowChooseDataset(false)
  }

  const currentDatasetInfo = useMemo(() => {
    if (!displayedDatasets || !value || !Array.isArray(value))
      return undefined
    return displayedDatasets.filter(dataset => value.some(v => v.id === dataset.id))
  }, [displayedDatasets, value])

  return (
    <>
      <PortalToFollowElem
        placement={placement}
        offset={offset}
        open={isShow}
        onOpenChange={onShowChange}
      >
        <PortalToFollowElemTrigger
          className='w-full'
          onClick={handleTriggerClick}
        >
          <DatasetTrigger
            open={isShow}
            datasetDetail={currentDatasetInfo}
          />
        </PortalToFollowElemTrigger>
        <PortalToFollowElemContent className='z-[1000]'>
          <div className="relative min-h-20 w-[389px] rounded-xl border-[0.5px] border-components-panel-border bg-components-panel-bg-blur shadow-lg backdrop-blur-sm">
            <div className='flex flex-col gap-1 px-4 py-3'>
              <div className='system-sm-semibold flex h-6 items-center text-text-secondary'>{t('app.appSelector.label')}</div>
              <DatasetPicker
                placement='bottom'
                offset={offset}
                trigger={
                  <DatasetTrigger
                    open={isShowChooseDataset}
                    datasetDetail={currentDatasetInfo}
                  />
                }
                isShow={isShowChooseDataset}
                onShowChange={setIsShowChooseDataset}
                disabled={false}
                onSelect={handleSelectDataset}
                scope={scope || 'all'}
                datasets={displayedDatasets}
                isLoading={isLoading || isLoadingMore}
                hasMore={hasMore}
                onLoadMore={handleLoadMore}
                searchText={searchText}
                onSearchChange={setSearchText}
                value={value}
              />
            </div>
          </div>
        </PortalToFollowElemContent>
      </PortalToFollowElem>
    </>
  )
}

export default React.memo(DatasetSelector)
