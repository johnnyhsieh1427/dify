'use client'
import type { FC } from 'react'
import React, { useCallback, useEffect, useRef } from 'react'
import {
  PortalToFollowElem,
  PortalToFollowElemContent,
  PortalToFollowElemTrigger,
} from '@/app/components/base/portal-to-follow-elem'
import type {
  OffsetOptions,
  Placement,
} from '@floating-ui/react'
import { Folder } from '@/app/components/base/icons/src/vender/solid/files'
import Input from '@/app/components/base/input'
import type { DataSet } from '@/models/datasets'
import type { UploadFiles } from '@/models/uploadfile'
import { useTranslation } from 'react-i18next'
import { fetchAllDocuments } from '@/service/knowledge/use-document'
import { RiCheckLine } from '@remixicon/react'
import cn from '@/utils/classnames'

type Props = {
  scope: string
  disabled: boolean
  trigger: React.ReactNode
  placement?: Placement
  offset?: OffsetOptions
  isShow: boolean
  onShowChange: (isShow: boolean) => void
  onSelect: (selectedDatasets: (DataSet & { documents: UploadFiles[] })[]) => void
  datasets: DataSet[]
  isLoading: boolean
  hasMore: boolean
  onLoadMore: () => void
  searchText: string
  onSearchChange: (text: string) => void
  value?: (DataSet & { documents: UploadFiles[] })[]
}

const DatasetPicker: FC<Props> = ({
  scope,
  disabled,
  trigger,
  placement = 'right-start',
  offset = 0,
  isShow,
  onShowChange,
  onSelect,
  datasets,
  isLoading,
  hasMore,
  onLoadMore,
  searchText,
  onSearchChange,
  value,
}) => {
  const { t } = useTranslation()
  const observerTarget = useRef<HTMLDivElement>(null)
  const observerRef = useRef<IntersectionObserver | null>(null)
  const loadingRef = useRef(false)

  const getDatasetDocs = useCallback(async (dataset: DataSet, selectedDatasets?: (DataSet & { documents: UploadFiles[] })[]) => {
    try {
      const docs = await fetchAllDocuments(dataset.id)
      if (docs && Array.isArray(docs)) {
        if (selectedDatasets?.some(v => v.id === dataset.id)) {
          // Remove the dataset if already selected
          return selectedDatasets.filter(v => v.id !== dataset.id)
        }
        else {
          return [
            ...(selectedDatasets || []),
            { ...dataset, documents: docs },
          ]
        }
      }
      return selectedDatasets || []
    }
    catch (error) {
      console.error('Error fetching dataset documents:', error)
      return selectedDatasets || []
    }
  }, [])

  const handleIntersection = useCallback((entries: IntersectionObserverEntry[]) => {
    const target = entries[0]
    if (!target.isIntersecting || loadingRef.current || !hasMore || isLoading) return

    loadingRef.current = true
    onLoadMore()
    // Reset loading state
    setTimeout(() => {
      loadingRef.current = false
    }, 500)
  }, [hasMore, isLoading, onLoadMore])

  useEffect(() => {
    if (!isShow) {
      if (observerRef.current) {
        observerRef.current.disconnect()
        observerRef.current = null
      }
      return
    }

    let mutationObserver: MutationObserver | null = null

    const setupIntersectionObserver = () => {
      if (!observerTarget.current) return

      // Create new observer
      observerRef.current = new IntersectionObserver(handleIntersection, {
        root: null,
        rootMargin: '100px',
        threshold: 0.1,
      })

      observerRef.current.observe(observerTarget.current)
    }

    // Set up MutationObserver to watch DOM changes
    mutationObserver = new MutationObserver((mutations) => {
      if (observerTarget.current) {
        setupIntersectionObserver()
        mutationObserver?.disconnect()
      }
    })

    // Watch body changes since Portal adds content to body
    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true,
    })

    // If element exists, set up IntersectionObserver directly
    if (observerTarget.current)
      setupIntersectionObserver()

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
        observerRef.current = null
      }
      mutationObserver?.disconnect()
    }
  }, [isShow, handleIntersection])

  const handleTriggerClick = () => {
    if (disabled) return
    onShowChange(true)
  }

  return (
    <PortalToFollowElem
      placement={placement}
      offset={offset}
      open={isShow}
      onOpenChange={onShowChange}
    >
      <PortalToFollowElemTrigger
        onClick={handleTriggerClick}
      >
        {trigger}
      </PortalToFollowElemTrigger>

      <PortalToFollowElemContent className='z-[1000]'>
        <div className="relative flex max-h-[400px] min-h-20 w-[356px] flex-col rounded-xl border-[0.5px] border-components-panel-border bg-components-panel-bg-blur shadow-lg backdrop-blur-sm">
          <div className='p-2 pb-1'>
            <Input
              showLeftIcon
              showClearIcon
              value={searchText}
              onChange={e => onSearchChange(e.target.value)}
              onClear={() => onSearchChange('')}
            />
          </div>
          <div className='min-h-0 flex-1 overflow-y-auto p-1'>
            {datasets.map(dataset => (
              <div
                key={dataset.id}
                className='flex cursor-pointer items-center gap-3 rounded-lg py-1 pl-2 pr-3 hover:bg-state-base-hover'
                onClick={async () => {
                  const selectedDatasets = await getDatasetDocs(dataset, value)
                  onSelect(selectedDatasets)
                }}
              >
                <Folder className='h-5 w-5 text-[#444CE7]' />
                <div title={dataset.name} className='system-sm-medium grow text-components-input-text-filled'>{dataset.name}</div>
                {value?.some(v => v.id === dataset.id) && (
                  <RiCheckLine className={cn('ml-0.5 h-4 w-4 shrink-0 text-text-quaternary group-hover:text-text-secondary')} />
                )}
              </div>
            ))}
            <div ref={observerTarget} className='h-4 w-full'>
              {isLoading && (
                <div className='flex justify-center py-2'>
                  <div className='text-sm text-gray-500'>{t('common.loading')}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </PortalToFollowElemContent>
    </PortalToFollowElem>
  )
}

export default React.memo(DatasetPicker)
