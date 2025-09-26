// 修改日期2025-07-31
// 新增app list的資料到WebAppStore(全域變數)
'use client'

import type { ChatConfig } from '@/app/components/base/chat/types'
import Loading from '@/app/components/base/loading'
import { checkOrSetAccessToken, checkUserAppLogin } from '@/app/components/share/utils'
import { AccessMode } from '@/models/access-control'
import type { AppData, AppMeta } from '@/models/share'
import { useGetWebAppAccessModeByCode } from '@/service/use-share'
import { usePathname, useSearchParams } from 'next/navigation'
import type { FC, PropsWithChildren } from 'react'
import { useEffect } from 'react'
import { useState } from 'react'
import { create } from 'zustand'
import { useGlobalPublicStore } from './global-public-context'

type WebAppStore = {
  shareCode: string | null
  updateShareCode: (shareCode: string | null) => void
  appInfo: AppData | null
  updateAppInfo: (appInfo: AppData | null) => void
  appParams: ChatConfig | null
  updateAppParams: (appParams: ChatConfig | null) => void
  webAppAccessMode: AccessMode
  updateWebAppAccessMode: (accessMode: AccessMode) => void
  appMeta: AppMeta | null
  updateWebAppMeta: (appMeta: AppMeta | null) => void
  userCanAccessApp: boolean
  updateUserCanAccessApp: (canAccess: boolean) => void
  appInfoList: AppData[] | null
  updateAppInfoList: (appInfoList: AppData[] | null) => void
  appParamsList: ChatConfig[] | null
  updateAppParamsList: (appParamsList: ChatConfig[] | null) => void
  appMetaList: AppMeta[] | null
  updateAppMetaList: (appMetaList: AppMeta[] | null) => void
  activeIndex: number
  setActiveIndex: (index: number) => void
}

export const useWebAppStore = create<WebAppStore>(set => ({
  shareCode: null,
  updateShareCode: (shareCode: string | null) => set(() => ({ shareCode })),
  appInfo: null,
  updateAppInfo: (appInfo: AppData | null) => set(() => ({ appInfo })),
  appParams: null,
  updateAppParams: (appParams: ChatConfig | null) => set(() => ({ appParams })),
  webAppAccessMode: AccessMode.SPECIFIC_GROUPS_MEMBERS,
  updateWebAppAccessMode: (accessMode: AccessMode) => set(() => ({ webAppAccessMode: accessMode })),
  appMeta: null,
  updateWebAppMeta: (appMeta: AppMeta | null) => set(() => ({ appMeta })),
  userCanAccessApp: false,
  updateUserCanAccessApp: (canAccess: boolean) => set(() => ({ userCanAccessApp: canAccess })),
  appInfoList: null,
  updateAppInfoList: (appInfoList: AppData[] | null) => set(() => ({ appInfoList })),
  appParamsList: null,
  updateAppParamsList: (appParamsList: ChatConfig[] | null) => set(() => ({ appParamsList })),
  appMetaList: null,
  updateAppMetaList: (appMetaList: AppMeta[] | null) => set(() => ({ appMetaList })),
  activeIndex: 0,
  setActiveIndex: (index: number) => set(() => ({ activeIndex: index })),
}))

const getShareCodeFromRedirectUrl = (redirectUrl: string | null): string | null => {
  if (!redirectUrl || redirectUrl.length === 0)
    return null
  const url = new URL(`${window.location.origin}${decodeURIComponent(redirectUrl)}`)
  return url.pathname.split('/').pop() || null
}
const getShareCodeFromPathname = (pathname: string): string | null => {
  const code = pathname.split('/').pop() || null
  if (code === 'webapp-signin')
    return null
  return code
}

const WebAppStoreProvider: FC<PropsWithChildren> = ({ children }) => {
  const isGlobalPending = useGlobalPublicStore(s => s.isGlobalPending)
  const updateWebAppAccessMode = useWebAppStore(state => state.updateWebAppAccessMode)
  const updateShareCode = useWebAppStore(state => state.updateShareCode)
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const redirectUrlParam = searchParams.get('redirect_url')

  // Compute shareCode directly
  const shareCode = getShareCodeFromRedirectUrl(redirectUrlParam) || getShareCodeFromPathname(pathname)
  useEffect(() => {
    updateShareCode(shareCode)
  }, [shareCode, updateShareCode])

  const { isFetching, data: accessModeResult } = useGetWebAppAccessModeByCode(shareCode)
  const [isFetchingAccessToken, setIsFetchingAccessToken] = useState(true)

  useEffect(() => {
    if (accessModeResult?.accessMode) {
      updateWebAppAccessMode(accessModeResult.accessMode)
      if (accessModeResult.accessMode === AccessMode.PUBLIC) {
        setIsFetchingAccessToken(true)
        if (shareCode === 'chat-app') {
          checkUserAppLogin().finally(() => {
            setIsFetchingAccessToken(false)
          })
        }
        else {
          checkOrSetAccessToken(shareCode).finally(() => {
            setIsFetchingAccessToken(false)
          })
        }
      }
      else {
        setIsFetchingAccessToken(false)
      }
    }
  }, [accessModeResult, updateWebAppAccessMode, shareCode])

  if (isGlobalPending || isFetching || isFetchingAccessToken) {
    return <div className='flex h-full w-full items-center justify-center'>
      <Loading />
    </div>
  }
  return (
    <>
      {children}
    </>
  )
}
export default WebAppStoreProvider
