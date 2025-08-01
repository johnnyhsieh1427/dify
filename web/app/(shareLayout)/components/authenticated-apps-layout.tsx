// 修改日期: 2025-08-01
// SWR載入資料前會先checkUserAppLogin檢查使用者登入狀態
'use client'

import AppUnavailable from '@/app/components/base/app-unavailable'
import Loading from '@/app/components/base/loading'
import { checkUserAppLogin, removeAccessToken } from '@/app/components/share/utils'
import { useWebAppStore } from '@/context/web-app-context'
import { fetchUserAppInfo, fetchUserAppMeta, fetchUserAppParams } from '@/service/share'
import { useRouter } from 'next/navigation'
import React, { useCallback, useEffect, useState } from 'react'
import useSWR from 'swr'

const AuthenticatedAppsLayout = ({ children }: { children: React.ReactNode }) => {
  const updateAppInfoList = useWebAppStore(s => s.updateAppInfoList)
  const updateAppParamsList = useWebAppStore(s => s.updateAppParamsList)
  const updateAppMetaList = useWebAppStore(s => s.updateAppMetaList)

  const router = useRouter()
  const [isAuthChecked, setIsAuthChecked] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const getSigninUrl = useCallback(() => {
    return '/signin'
  }, [])

  const backToHome = useCallback(() => {
    removeAccessToken()
    router.replace(getSigninUrl())
  }, [getSigninUrl, router])

  useEffect(() => {
    (async () => {
      try {
        await checkUserAppLogin()
        setIsAuthenticated(true)
      }
      catch {
        backToHome()
      }
      finally {
        setIsAuthChecked(true)
      }
    })()
  }, [backToHome])

  const { data: appInfoList, isLoading: isLoadingAppInfos, error: appInfoError } = useSWR(
    isAuthenticated ? 'appInfoList' : null, fetchUserAppInfo, { revalidateOnFocus: false })
  const { data: appParamsList, isLoading: isLoadingAppParams, error: appParamsError } = useSWR(
    isAuthenticated ? 'appParamsList' : null, fetchUserAppParams, { revalidateOnFocus: false })
  const { data: appMetaList, isLoading: isLoadingAppMeta, error: appMetaError } = useSWR(
    isAuthenticated ? 'appMetaList' : null, fetchUserAppMeta, { revalidateOnFocus: false })

  useEffect(() => {
    if (appInfoList) updateAppInfoList(appInfoList)
    if (appParamsList) updateAppParamsList(appParamsList)
    if (appMetaList) updateAppMetaList(appMetaList)
  }, [appInfoList, appParamsList, appMetaList, updateAppInfoList, updateAppParamsList, updateAppMetaList])

  if (!isAuthChecked || isLoadingAppInfos || isLoadingAppParams || isLoadingAppMeta)
    return <div className='flex h-full items-center justify-center'><Loading /></div>

  if (appInfoError || appParamsError || appMetaError) {
    const msg = appInfoError?.message ?? appParamsError?.message ?? appMetaError?.message
    return <div className='flex h-full items-center justify-center'>
      <AppUnavailable unknownReason={msg!} />
    </div>
  }

  return <>{children}</>
}

export default React.memo(AuthenticatedAppsLayout)
