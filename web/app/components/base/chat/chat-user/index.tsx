// 修改日期2025-01-20
// 修改內容：
// 將原有的function checkOrSetAccessToken改成checkIsLogin
// 修改日期2025-02-28
// 新增給web-chat介面使用
// 修改日期2025-05-27
// 新增mutate方法，清除appInfos、appParamsList、appMetaList的快取
// 修改日期2025-07-23
// 更新符合最新的ChatWithHistoryContextValue定義

import type { FC } from 'react'
import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import { useAsyncEffect } from 'ahooks'
import { useThemeContext } from '../embedded-chatbot/theme/theme-context'
import {
  ChatWithHistoryContext,
  useChatWithHistoryContext,
} from './context'
import { useChatWithHistory } from './hooks'
import Sidebar from './sidebar'
import Header from './header'
import HeaderInMobile from './header-in-mobile'
import ChatWrapper from './chat-wrapper'
import type { InstalledApp } from '@/models/explore'
import Loading from '@/app/components/base/loading'
import useBreakpoints, { MediaType } from '@/hooks/use-breakpoints'
import { checkUserAppLogin, removeAccessToken } from '@/app/components/share/utils'
import AppUnavailable from '@/app/components/base/app-unavailable'
import cn from '@/utils/classnames'
import useDocumentTitle from '@/hooks/use-document-title'
import { CONVERSATION_ID_INFO } from '../constants'
import { mutate } from 'swr'
import { useTranslation } from 'react-i18next'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'

type ChatWithHistoryProps = {
  className?: string
}
const ChatWithHistory: FC<ChatWithHistoryProps> = ({
  className,
}) => {
  const {
    userCanAccess,
    appInfoError,
    appData,
    appInfoLoading,
    appChatListDataLoading,
    chatShouldReloadKey,
    isMobile,
    themeBuilder,
    sidebarCollapseState,
  } = useChatWithHistoryContext()
  const isSidebarCollapsed = sidebarCollapseState
  const customConfig = appData?.custom_config
  const site = appData?.site

  const [showSidePanel, setShowSidePanel] = useState(false)

  useEffect(() => {
    themeBuilder?.buildTheme(site?.chat_color_theme, site?.chat_color_theme_inverted)
  }, [site, customConfig, themeBuilder])
  useDocumentTitle(site?.title || 'Chat')

  const { t } = useTranslation()
  const searchParams = useSearchParams()
  const router = useRouter()
  const pathname = usePathname()
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

  if (appInfoLoading) {
    return (
      <Loading type='app' />
    )
  }
  // if (!userCanAccess) {
  //   return <div className='flex h-full flex-col items-center justify-center gap-y-2'>
  //     <AppUnavailable className='h-auto w-auto' code={403} unknownReason='no permission.' />
  //     {!isInstalledApp && <span className='system-sm-regular cursor-pointer text-text-tertiary' onClick={backToHome}>{t('common.userProfile.logout')}</span>}
  //   </div>
  // }

  if (appInfoError) {
    return (
      <AppUnavailable />
    )
  }

  return (
    <div className={cn(
      'flex h-full bg-background-default-burn',
      isMobile && 'flex-col',
      className,
    )}>
      {!isMobile && (
        <div className={cn(
          'flex w-[236px] flex-col p-1 pr-0 transition-all duration-200 ease-in-out',
          isSidebarCollapsed && 'w-0 overflow-hidden !p-0',
        )}>
          <Sidebar />
        </div>
      )}
      {isMobile && (
        <HeaderInMobile />
      )}
      <div className={cn('relative grow p-2', isMobile && 'h-[calc(100%_-_56px)] p-0')}>
        {isSidebarCollapsed && (
          <div
            className={cn(
              'absolute top-0 z-20 flex h-full w-[256px] flex-col p-2 transition-all duration-500 ease-in-out',
              showSidePanel ? 'left-0' : 'left-[-248px]',
            )}
            onMouseEnter={() => setShowSidePanel(true)}
            onMouseLeave={() => setShowSidePanel(false)}
          >
            <Sidebar isPanel />
          </div>
        )}
        <div className={cn('flex h-full flex-col overflow-hidden border-[0,5px] border-components-panel-border-subtle bg-chatbot-bg', isMobile ? 'rounded-t-2xl' : 'rounded-2xl')}>
          {!isMobile && <Header />}
          {appChatListDataLoading && (
            <Loading type='app' />
          )}
          {!appChatListDataLoading && (
            <ChatWrapper key={chatShouldReloadKey} />
          )}
        </div>
      </div>
    </div>
  )
}

export type ChatWithHistoryWrapProps = {
  installedAppInfo?: InstalledApp
  className?: string
}
const ChatWithHistoryWrap: FC<ChatWithHistoryWrapProps> = ({
  installedAppInfo,
  className,
}) => {
  const media = useBreakpoints()
  const isMobile = media === MediaType.mobile
  const themeBuilder = useThemeContext()

  const {
    appInfoError,
    appInfoLoading,
    userCanAccess,
    appData,
    appDataList,
    appParams,
    appMeta,
    appChatListDataLoading,
    currentConversationId,
    currentConversationItem,
    appPrevChatTree,
    pinnedConversationList,
    conversationList,
    newConversationInputs,
    newConversationInputsRef,
    handleNewConversationInputsChange,
    inputsForms,
    handleNewConversation,
    handleStartChat,
    handleChangeConversation,
    handlePinConversation,
    handleUnpinConversation,
    handleDeleteConversation,
    conversationRenaming,
    handleRenameConversation,
    handleNewConversationCompleted,
    chatShouldReloadKey,
    isInstalledApp,
    appId,
    handleFeedback,
    currentChatInstanceRef,
    sidebarCollapseState,
    handleSidebarCollapse,
    clearChatList,
    setClearChatList,
    isResponding,
    setIsResponding,
    currentConversationInputs,
    setCurrentConversationInputs,
    allInputsHidden,
    activeIndex,
    setActiveIndex,
  } = useChatWithHistory(installedAppInfo)

  return (
    <ChatWithHistoryContext.Provider value={{
      appInfoError,
      appInfoLoading,
      appData,
      userCanAccess,
      appDataList,
      appParams,
      appMeta,
      appChatListDataLoading,
      currentConversationId,
      currentConversationItem,
      appPrevChatTree,
      pinnedConversationList,
      conversationList,
      newConversationInputs,
      newConversationInputsRef,
      handleNewConversationInputsChange,
      inputsForms,
      handleNewConversation,
      handleStartChat,
      handleChangeConversation,
      handlePinConversation,
      handleUnpinConversation,
      handleDeleteConversation,
      conversationRenaming,
      handleRenameConversation,
      handleNewConversationCompleted,
      chatShouldReloadKey,
      isMobile,
      isInstalledApp,
      appId,
      handleFeedback,
      currentChatInstanceRef,
      themeBuilder,
      sidebarCollapseState,
      handleSidebarCollapse,
      clearChatList,
      setClearChatList,
      isResponding,
      setIsResponding,
      currentConversationInputs,
      setCurrentConversationInputs,
      allInputsHidden,
      activeIndex,
      setActiveIndex,
    }}>
      <ChatWithHistory className={className} />
    </ChatWithHistoryContext.Provider>
  )
}

const ChatWithHistoryWrapWithCheckToken: FC<ChatWithHistoryWrapProps> = ({
  installedAppInfo,
  className,
}) => {
  const [initialized, setInitialized] = useState(false)
  const [appUnavailable, setAppUnavailable] = useState<boolean>(false)
  const [isUnknownReason, setIsUnknownReason] = useState<boolean>(false)

  useAsyncEffect(async () => {
    if (!initialized) {
      if (!installedAppInfo) {
        try {
          localStorage.removeItem(CONVERSATION_ID_INFO)
          mutate(() => true, undefined, { revalidate: false })
          // ✅ 或者只清除特定 key
          mutate('appInfos', undefined, { revalidate: false })
          mutate('appParamsList', undefined, { revalidate: false })
          mutate('appMetaList', undefined, { revalidate: false })
          await checkUserAppLogin()
        }
        catch (e: any) {
          (e.status !== 404) && setIsUnknownReason(true)
          setAppUnavailable(true)
        }
      }
      setInitialized(true)
    }
  }, [])

  if (!initialized)
    return null

  if (appUnavailable)
    return <AppUnavailable isUnknownReason={isUnknownReason} />

  return (
    <ChatWithHistoryWrap
      installedAppInfo={installedAppInfo}
      className={className}
    />
  )
}

export default ChatWithHistoryWrapWithCheckToken
