// 修改日期2025-01-20
// 修改內容：
// 增加function checkAppTenantPermission和checkIsLogin
// 確認使用者登入狀態和使用者是否在app的tenant權限
// 修改日期2025-02-28
// 新增給web-chat介面使用

'use client'
import React, { useState } from 'react'
import ChatWithHistoryWrap from '@/app/components/base/chat/chat-user'
import AuthenticatedAppsLayout from '../components/authenticated-apps-layout'
import { useAsyncEffect } from 'ahooks'
import { useRouter } from 'next/navigation'
import { checkUserAppLogin } from '@/app/components/share/utils'

const Chat = () => {
  const router = useRouter()
  const [isLogin, setLogin] = useState<boolean>(true)
  const [initialized, setInitialized] = useState(false)

  useAsyncEffect(async () => {
    if (!initialized) {
      try {
        await checkUserAppLogin()
        setInitialized(true)
      }
      catch {
        setLogin(false)
      }
    }
  }, [initialized])

  if (!isLogin)
    router.push('/signin')

  return (
    <AuthenticatedAppsLayout>
      <ChatWithHistoryWrap />
    </AuthenticatedAppsLayout>
  )
}

export default React.memo(Chat)
