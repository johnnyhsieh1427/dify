// 修改日期2025-01-20
// 修改內容：
// 增加function checkAppTenantPermission和checkIsLogin
// 確認使用者登入狀態和使用者是否在app的tenant權限
// 修改日期2025-02-28
// 新增給web-chat介面使用

'use client'
import React, { useState } from 'react'
import { useAsyncEffect } from 'ahooks'
import { useRouter } from 'next/navigation'
import { checkUserAppLogin } from '@/app/components/share/utils'
import ChatWithHistoryWrap from '@/app/components/base/chat/chat-user'

const Chat = () => {
  const router = useRouter()
  const [initialized, setInitialized] = useState(false)
  const [isLogin, setLogin] = useState<boolean>(true)

  useAsyncEffect(async () => {
    if (!initialized) {
      try {
        await checkUserAppLogin()
      }
      catch (e: any) {
        setLogin(false)
      }
    }
    setInitialized(true)
  }, [])

  if (!initialized)
    return null

  if (!isLogin)
    router.push('/signin')

  return (
    <ChatWithHistoryWrap />
  )
}

export default React.memo(Chat)
