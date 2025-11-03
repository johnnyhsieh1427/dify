'use client'
import { useEducationInit } from '@/app/education-apply/hooks'
import List from './list'
import useDocumentTitle from '@/hooks/use-document-title'
import { useTranslation } from 'react-i18next'
import { useAppContext } from '@/context/app-context'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

const Apps = () => {
  const { t } = useTranslation()
  const router = useRouter()
  const { isCurrentWorkspaceOwner, isCurrentWorkspaceManager, isCurrentWorkspaceDatasetOperator, isInitialized } = useAppContext()

  useDocumentTitle(t('common.menus.apps'))
  useEducationInit()

  useEffect(() => {
    if (isInitialized) {
      if (!(isCurrentWorkspaceOwner || isCurrentWorkspaceManager || isCurrentWorkspaceDatasetOperator))
        router.replace('/chat-app')
    }
  }, [isCurrentWorkspaceOwner, isCurrentWorkspaceManager, isCurrentWorkspaceDatasetOperator, isInitialized])
  return (
    <div className='relative flex h-0 shrink-0 grow flex-col overflow-y-auto bg-background-body'>
      <List />
    </div >
  )
}

export default Apps
