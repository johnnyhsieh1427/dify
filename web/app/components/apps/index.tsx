// 修改日期2025/07/29
// 使用isCurrentWorkspaceOwner, isCurrentWorkspaceManager, isInitialized來判斷初始化和使用角色
'use client'
import { useEducationInit } from '@/app/education-apply/hooks'
import { useGlobalPublicStore } from '@/context/global-public-context'
import List from './list'
import Footer from './footer'
import useDocumentTitle from '@/hooks/use-document-title'
import { useTranslation } from 'react-i18next'
import { useAppContext } from '@/context/app-context'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
const Apps = () => {
  const { t } = useTranslation()
  const router = useRouter()
  const { systemFeatures } = useGlobalPublicStore()
  const { isCurrentWorkspaceOwner, isCurrentWorkspaceManager, isInitialized } = useAppContext()
  useEffect(() => {
    if (isInitialized) {
      if (!(isCurrentWorkspaceOwner || isCurrentWorkspaceManager))
        router.replace('/chat-app')
    }
  }, [isCurrentWorkspaceOwner, isCurrentWorkspaceManager, isInitialized])
  useDocumentTitle(t('common.menus.apps'))
  useEducationInit()

  return (
    <div className='relative flex h-0 shrink-0 grow flex-col overflow-y-auto bg-background-body'>
      <List />
      {!systemFeatures.branding.enabled && (
        <Footer />
      )}
    </div >
  )
}

export default Apps
