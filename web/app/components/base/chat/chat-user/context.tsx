// 修改日期2025-02-28
// 新增給web-chat介面使用

// 修改日期2025-03-13
// 修改ChatItem為ChatItemInTree, appPrevChatList為appPrevChatTree

// 修改日期2025-07-23
// 更新符合最新的ChatWithHistoryContextValue定義

'use client'

import type { RefObject } from 'react'
import { createContext, useContext } from 'use-context-selector'
import type {
  Callback,
  ChatConfig,
  ChatItemInTree,
  Feedback,
} from '../types'
import type { ThemeBuilder } from '../embedded-chatbot/theme/theme-context'
import type {
  AppConversationData,
  AppData,
  AppMeta,
  ConversationItem,
} from '@/models/share'
import { noop } from 'lodash-es'

export type ChatWithHistoryContextValue = {
  appInfoError?: any
  appInfoLoading?: boolean
  appMeta?: AppMeta
  appData?: AppData
  appDataList?: AppData[]
  userCanAccess?: boolean
  appParams?: ChatConfig
  appChatListDataLoading?: boolean
  currentConversationId: string
  currentConversationItem?: ConversationItem
  appPrevChatTree: ChatItemInTree[]
  pinnedConversationList: AppConversationData['data']
  conversationList: AppConversationData['data']
  newConversationInputs: Record<string, any>
  newConversationInputsRef: RefObject<Record<string, any>>
  handleNewConversationInputsChange: (v: Record<string, any>) => void
  inputsForms: any[]
  handleNewConversation: () => void
  handleStartChat: (callback?: any) => void
  handleChangeConversation: (conversationId: string) => void
  handlePinConversation: (conversationId: string) => void
  handleUnpinConversation: (conversationId: string) => void
  handleDeleteConversation: (conversationId: string, callback: Callback) => void
  conversationRenaming: boolean
  handleRenameConversation: (conversationId: string, newName: string, callback: Callback) => void
  handleNewConversationCompleted: (newConversationId: string) => void
  chatShouldReloadKey: string
  isMobile: boolean
  isInstalledApp: boolean
  appId?: string
  handleFeedback: (messageId: string, feedback: Feedback) => void
  currentChatInstanceRef: RefObject<{ handleStop: () => void }>
  themeBuilder?: ThemeBuilder
  sidebarCollapseState?: boolean
  handleSidebarCollapse: (state: boolean) => void
  clearChatList?: boolean
  setClearChatList: (state: boolean) => void
  isResponding?: boolean
  setIsResponding: (state: boolean) => void,
  currentConversationInputs: Record<string, any> | null,
  setCurrentConversationInputs: (v: Record<string, any>) => void,
  allInputsHidden: boolean,
  activeIndex?: number
  setActiveIndex: (index: number) => void
}

export const ChatWithHistoryContext = createContext<ChatWithHistoryContextValue>({
  userCanAccess: false,
  currentConversationId: '',
  appPrevChatTree: [],
  pinnedConversationList: [],
  conversationList: [],
  newConversationInputs: {},
  newConversationInputsRef: { current: {} },
  handleNewConversationInputsChange: noop,
  inputsForms: [],
  handleNewConversation: noop,
  handleStartChat: noop,
  handleChangeConversation: noop,
  handlePinConversation: noop,
  handleUnpinConversation: noop,
  handleDeleteConversation: noop,
  conversationRenaming: false,
  handleRenameConversation: noop,
  handleNewConversationCompleted: noop,
  chatShouldReloadKey: '',
  isMobile: false,
  isInstalledApp: false,
  handleFeedback: noop,
  currentChatInstanceRef: { current: { handleStop: noop } },
  sidebarCollapseState: false,
  handleSidebarCollapse: noop,
  clearChatList: false,
  setClearChatList: noop,
  isResponding: false,
  setIsResponding: noop,
  currentConversationInputs: {},
  setCurrentConversationInputs: noop,
  allInputsHidden: false,
  activeIndex: 0,
  setActiveIndex: noop,
})
export const useChatWithHistoryContext = () => useContext(ChatWithHistoryContext)
