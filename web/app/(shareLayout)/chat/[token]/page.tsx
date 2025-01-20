// 修改日期2025-01-20
// 修改內容：
// 增加function checkAppTenantPermission和checkIsLogin
// 確認使用者登入狀態和使用者是否在app的tenant權限
'use client'
import React, { useState } from 'react'
import { useAsyncEffect } from 'ahooks'
import { useRouter } from 'next/navigation'
import { checkAppTenantPermission, checkIsLogin } from '@/app/components/share/utils'
import ChatWithHistoryWrap from '@/app/components/base/chat/chat-with-history'

const Chat = () => {
  const router = useRouter()
  const [initialized, setInitialized] = useState(false)
  const [isLogin, setLogin] = useState<boolean>(true)
  const [isAuthorized, setAuthorized] = useState<boolean>(true)

  useAsyncEffect(async () => {
    if (!initialized) {
      try {
        await Promise.all([checkIsLogin(), checkAppTenantPermission()])
      }
      catch (e: any) {
        if (e.status === 403) {
          setAuthorized(false)
        }
        else if (e.status === 401) {
          setLogin(false)
        }
        else {
          setLogin(false)
          setAuthorized(false)
        }
      }
    }
    setInitialized(true)
  }, [])

  if (!initialized)
    return null

  if (!isLogin)
    router.push('/signin')

  if (!isAuthorized)
    router.push('/apps')

  return (
    <ChatWithHistoryWrap />
  )
}

export default React.memo(Chat)
