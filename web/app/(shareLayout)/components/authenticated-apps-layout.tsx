'use client'

import AppUnavailable from '@/app/components/base/app-unavailable'
import Loading from '@/app/components/base/loading'
import { removeAccessToken } from '@/app/components/share/utils'
import { useWebAppStore } from '@/context/web-app-context'
import { fetchUserAppInfo, fetchUserAppMeta, fetchUserAppParams } from '@/service/share'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import React, { useCallback, useEffect } from 'react'
import useSWR from 'swr'

const AuthenticatedAppsLayout = ({ children }: { children: React.ReactNode }) => {
  const updateAppInfoList = useWebAppStore(s => s.updateAppInfoList)
  const updateAppParamsList = useWebAppStore(s => s.updateAppParamsList)
  const updateAppMetaList = useWebAppStore(s => s.updateAppMetaList)

  const { data: appInfoList, isLoading: isLoadingAppInfos, error: appInfoError } = useSWR('appInfoList', () => fetchUserAppInfo())
  const { data: appParamsList, isLoading: isLoadingAppParams, error: appParamsError } = useSWR('appParamsList', () => fetchUserAppParams())
  const { data: appMetaList, isLoading: isLoadingAppMeta, error: appMetaError } = useSWR('appMetaList', () => fetchUserAppMeta())

  useEffect(() => {
    if (appInfoList && appInfoList.length > 0)
      updateAppInfoList(appInfoList)
    if (appParamsList && appParamsList.length > 0)
      updateAppParamsList(appParamsList)
    if (appMetaList && appMetaList.length > 0)
      updateAppMetaList(appMetaList)
  }, [appInfoList, appParamsList, appMetaList, updateAppInfoList, updateAppParamsList, updateAppMetaList])

  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const getSigninUrl = useCallback(() => {
    const params = new URLSearchParams(searchParams)
    params.delete('message')
    params.set('redirect_url', pathname)
    return `/webapp-signin?${params.toString()}`
  }, [searchParams, pathname])

  const backToHome = useCallback(() => {
    removeAccessToken()
    const url = getSigninUrl()
    router.replace(url)
  }, [getSigninUrl, router])

  if (appInfoError) {
    return <div className='flex h-full items-center justify-center'>
      <AppUnavailable unknownReason={appInfoError.message} />
    </div>
  }
  if (appParamsError) {
    return <div className='flex h-full items-center justify-center'>
      <AppUnavailable unknownReason={appParamsError.message} />
    </div>
  }
  if (appMetaError) {
    return <div className='flex h-full items-center justify-center'>
      <AppUnavailable unknownReason={appMetaError.message} />
    </div>
  }
  if (isLoadingAppInfos || isLoadingAppParams || isLoadingAppMeta) {
    return <div className='flex h-full items-center justify-center'>
      <Loading />
    </div>
  }
  // if ((
  //   !Array.isArray(appInfoList) || appInfoList.length === 0
  // ) && (
  //   !Array.isArray(appMetaList) || appMetaList.length === 0
  // )) {
  //   return <div className='flex h-full flex-col items-center justify-center gap-y-2'>
  //     <AppUnavailable className='h-auto w-auto' code={403} unknownReason='no permission.' />
  //     <span className='system-sm-regular cursor-pointer text-text-tertiary' onClick={backToHome}>{t('common.userProfile.logout')}</span>
  //   </div>
  // }
  return <>{children}</>
}

export default React.memo(AuthenticatedAppsLayout)
