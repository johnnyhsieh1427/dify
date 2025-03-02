// 修改日期2025-02-28
// 新增給web-chat介面使用

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import { useTranslation } from 'react-i18next'
import useSWR from 'swr'
import { useLocalStorageState } from 'ahooks'
import produce from 'immer'
import type {
  Callback,
  ChatConfig,
  Feedback,
} from '../types'
import { CONVERSATION_ID_INFO } from '../constants'
import { getPrevChatList } from '../utils'
import {
  delConversation,
  fetchUserAppInfo,
  fetchUserAppMeta,
  fetchUserAppParams,
  fetchUserChatList,
  fetchUserConversations,
  generationUserConversationName,
  pinUserConversation,
  renameUserConversation,
  unpinUserConversation,
  // updateFeedback,
  updateUserFeedback,
} from '@/service/share'
import { useAppContext } from '@/context/app-context'

import type { InstalledApp } from '@/models/explore'
import type {
  ConversationItem,
} from '@/models/share'
import { useToastContext } from '@/app/components/base/toast'
import { changeLanguage } from '@/i18n/i18next-config'
import { useAppFavicon } from '@/hooks/use-app-favicon'
import { InputVarType } from '@/app/components/workflow/types'
import { TransferMethod } from '@/types/app'

export const useChatWithHistory = (installedAppInfo?: InstalledApp) => {
  // 一律改成isInstalledApp = False
  const isInstalledApp = false
  // const isInstalledApp = useMemo(() => !!installedAppInfo, [installedAppInfo])

  // 設定activeIndex，代表選擇哪個app
  const [activeIndex, setActiveIndex] = useState<number>(0)

  const { data: appInfos, isLoading: appInfoLoading, error: appInfoError } = useSWR('appInfos', () => fetchUserAppInfo())
  const appDataList = useMemo(() => appInfos?.items, [appInfos])
  const appInfo = useMemo(() => appDataList?.[activeIndex], [appDataList, activeIndex])
  const appData = useMemo(() => appInfo, [appInfo])
  const appId = useMemo(() => appData?.app_id || '00000000-0000-0000-0000-000000000000', [appData])
  // const { data: appInfo, isLoading: appInfoLoading, error: appInfoError } = useSWR(installedAppInfo ? null : 'appInfo', fetchAppInfo)

  const { userProfile } = useAppContext()

  useAppFavicon({
    enable: !installedAppInfo,
    icon_type: appInfo?.site.icon_type,
    icon: appInfo?.site.icon,
    icon_background: appInfo?.site.icon_background,
    icon_url: appInfo?.site.icon_url,
  })

  // useEffect(() => {
  //   if (appData?.site.default_language)
  //     changeLanguage(appData.site.default_language)
  // }, [appData])
  useEffect(() => {
    if (userProfile.interface_language)
      changeLanguage(userProfile.interface_language)
  }, [userProfile])

  const [conversationIdInfo, setConversationIdInfo] = useLocalStorageState<Record<string, string>>(CONVERSATION_ID_INFO, {
    defaultValue: {},
  })
  const currentConversationId = useMemo(() => conversationIdInfo?.[appId || ''] || '', [appId, conversationIdInfo])
  const handleConversationIdInfoChange = useCallback((changeConversationId: string) => {
    if (appId) {
      setConversationIdInfo({
        ...conversationIdInfo,
        [appId || '']: changeConversationId,
      })
    }
  }, [appId, conversationIdInfo, setConversationIdInfo])
  const [showConfigPanelBeforeChat, setShowConfigPanelBeforeChat] = useState(true)

  const [newConversationId, setNewConversationId] = useState('')
  const chatShouldReloadKey = useMemo(() => {
    if (currentConversationId === newConversationId)
      return ''

    return currentConversationId
  }, [currentConversationId, newConversationId])

  const { data: appParamsList } = useSWR('appParamsList', () => fetchUserAppParams())
  const { data: appMetaList } = useSWR('appMetaList', () => fetchUserAppMeta())
  // const { data: appParams } = useSWR(['appParams', isInstalledApp, appId], () => fetchAppParams(isInstalledApp, appId))
  // const { data: appMeta } = useSWR(['appMeta', isInstalledApp, appId], () => fetchAppMeta(isInstalledApp, appId))
  const appParams = useMemo(() => appParamsList?.[activeIndex], [appParamsList, activeIndex])
  const appMeta = useMemo(() => appMetaList?.[activeIndex], [appMetaList, activeIndex])

  const { data: appPinnedConversationData, mutate: mutateAppPinnedConversationData } = useSWR(['appConversationData', isInstalledApp, appId, true], () => fetchUserConversations(appId, undefined, true, 100))
  const { data: appConversationData, isLoading: appConversationDataLoading, mutate: mutateAppConversationData } = useSWR(['appConversationData', isInstalledApp, appId, false], () => fetchUserConversations(appId, undefined, false, 100))
  const { data: appChatListData, isLoading: appChatListDataLoading } = useSWR(chatShouldReloadKey ? ['appChatListData', chatShouldReloadKey, isInstalledApp, appId] : null, () => fetchUserChatList(appId, chatShouldReloadKey))

  const appPrevChatList = useMemo(
    () => (currentConversationId && appChatListData?.data.length)
      ? getPrevChatList(appChatListData.data)
      : [],
    [appChatListData, currentConversationId],
  )

  const [showNewConversationItemInList, setShowNewConversationItemInList] = useState(false)

  const pinnedConversationList = useMemo(() => {
    return appPinnedConversationData?.data || []
  }, [appPinnedConversationData])
  const { t } = useTranslation()
  const newConversationInputsRef = useRef<Record<string, any>>({})
  const [newConversationInputs, setNewConversationInputs] = useState<Record<string, any>>({})
  const handleNewConversationInputsChange = useCallback((newInputs: Record<string, any>) => {
    newConversationInputsRef.current = newInputs
    setNewConversationInputs(newInputs)
  }, [])
  const inputsForms = useMemo(() => {
    return (appParams?.user_input_form || []).filter((item: any) => !item.external_data_tool).map((item: any) => {
      if (item.paragraph) {
        return {
          ...item.paragraph,
          type: 'paragraph',
        }
      }
      if (item.number) {
        return {
          ...item.number,
          type: 'number',
        }
      }
      if (item.select) {
        return {
          ...item.select,
          type: 'select',
        }
      }

      if (item['file-list']) {
        return {
          ...item['file-list'],
          type: 'file-list',
        }
      }

      if (item.file) {
        return {
          ...item.file,
          type: 'file',
        }
      }

      return {
        ...item['text-input'],
        type: 'text-input',
      }
    })
  }, [appParams])
  useEffect(() => {
    const conversationInputs: Record<string, any> = {}

    inputsForms.forEach((item: any) => {
      conversationInputs[item.variable] = item.default || null
    })
    handleNewConversationInputsChange(conversationInputs)
  }, [handleNewConversationInputsChange, inputsForms])

  const { data: newConversation } = useSWR(newConversationId ? [isInstalledApp, appId, newConversationId] : null, () => generationUserConversationName(appId, newConversationId), { revalidateOnFocus: false })
  const [originConversationList, setOriginConversationList] = useState<ConversationItem[]>([])
  useEffect(() => {
    if (appConversationData?.data && !appConversationDataLoading)
      setOriginConversationList(appConversationData?.data)
  }, [appConversationData, appConversationDataLoading])
  const conversationList = useMemo(() => {
    const data = originConversationList.slice()

    if (showNewConversationItemInList && data[0]?.id !== '') {
      data.unshift({
        id: '',
        name: t('share.chat.newChatDefaultName'),
        inputs: {},
        introduction: '',
      })
    }
    return data
  }, [originConversationList, showNewConversationItemInList, t])

  useEffect(() => {
    if (newConversation) {
      setOriginConversationList(produce((draft) => {
        const index = draft.findIndex(item => item.id === newConversation.id)

        if (index > -1)
          draft[index] = newConversation
        else
          draft.unshift(newConversation)
      }))
    }
  }, [newConversation])

  const currentConversationItem = useMemo(() => {
    let conversationItem = conversationList.find(item => item.id === currentConversationId)

    if (!conversationItem && pinnedConversationList.length)
      conversationItem = pinnedConversationList.find(item => item.id === currentConversationId)

    return conversationItem
  }, [conversationList, currentConversationId, pinnedConversationList])

  const { notify } = useToastContext()
  const checkInputsRequired = useCallback((silent?: boolean) => {
    let hasEmptyInput = ''
    let fileIsUploading = false
    const requiredVars = inputsForms.filter(({ required }) => required)
    if (requiredVars.length) {
      requiredVars.forEach(({ variable, label, type }) => {
        if (hasEmptyInput)
          return

        if (fileIsUploading)
          return

        if (!newConversationInputsRef.current[variable] && !silent)
          hasEmptyInput = label as string

        if ((type === InputVarType.singleFile || type === InputVarType.multiFiles) && newConversationInputsRef.current[variable] && !silent) {
          const files = newConversationInputsRef.current[variable]
          if (Array.isArray(files))
            fileIsUploading = files.find(item => item.transferMethod === TransferMethod.local_file && !item.uploadedId)
          else
            fileIsUploading = files.transferMethod === TransferMethod.local_file && !files.uploadedId
        }
      })
    }

    if (hasEmptyInput) {
      notify({ type: 'error', message: t('appDebug.errorMessage.valueOfVarRequired', { key: hasEmptyInput }) })
      return false
    }

    if (fileIsUploading) {
      notify({ type: 'info', message: t('appDebug.errorMessage.waitForFileUpload') })
      return
    }

    return true
  }, [inputsForms, notify, t])
  const handleStartChat = useCallback(() => {
    if (checkInputsRequired()) {
      setShowConfigPanelBeforeChat(false)
      setShowNewConversationItemInList(true)
    }
  }, [setShowConfigPanelBeforeChat, setShowNewConversationItemInList, checkInputsRequired])
  const currentChatInstanceRef = useRef<{ handleStop: () => void }>({ handleStop: () => { } })
  const handleChangeConversation = useCallback((conversationId: string) => {
    currentChatInstanceRef.current.handleStop()
    setNewConversationId('')
    handleConversationIdInfoChange(conversationId)

    if (conversationId === '' && !checkInputsRequired(true))
      setShowConfigPanelBeforeChat(true)
    else
      setShowConfigPanelBeforeChat(false)
  }, [handleConversationIdInfoChange, setShowConfigPanelBeforeChat, checkInputsRequired])
  const handleNewConversation = useCallback(() => {
    currentChatInstanceRef.current.handleStop()
    setNewConversationId('')

    if (showNewConversationItemInList) {
      handleChangeConversation('')
    }
    else if (currentConversationId) {
      handleConversationIdInfoChange('')
      setShowConfigPanelBeforeChat(true)
      setShowNewConversationItemInList(true)
      handleNewConversationInputsChange({})
    }
  }, [handleChangeConversation, currentConversationId, handleConversationIdInfoChange, setShowConfigPanelBeforeChat, setShowNewConversationItemInList, showNewConversationItemInList, handleNewConversationInputsChange])
  const handleUpdateConversationList = useCallback(() => {
    mutateAppConversationData()
    mutateAppPinnedConversationData()
  }, [mutateAppConversationData, mutateAppPinnedConversationData])

  const handlePinConversation = useCallback(async (conversationId: string) => {
    await pinUserConversation(appId, conversationId)
    notify({ type: 'success', message: t('common.api.success') })
    handleUpdateConversationList()
  }, [appId, notify, t, handleUpdateConversationList])

  const handleUnpinConversation = useCallback(async (conversationId: string) => {
    await unpinUserConversation(appId, conversationId)
    notify({ type: 'success', message: t('common.api.success') })
    handleUpdateConversationList()
  }, [appId, notify, t, handleUpdateConversationList])

  const [conversationDeleting, setConversationDeleting] = useState(false)
  const handleDeleteConversation = useCallback(async (
    conversationId: string,
    {
      onSuccess,
    }: Callback,
  ) => {
    if (conversationDeleting)
      return

    try {
      setConversationDeleting(true)
      await delConversation(isInstalledApp, appId, conversationId)
      notify({ type: 'success', message: t('common.api.success') })
      onSuccess()
    }
    finally {
      setConversationDeleting(false)
    }

    if (conversationId === currentConversationId)
      handleNewConversation()

    handleUpdateConversationList()
  }, [isInstalledApp, appId, notify, t, handleUpdateConversationList, handleNewConversation, currentConversationId, conversationDeleting])

  const [conversationRenaming, setConversationRenaming] = useState(false)
  const handleRenameConversation = useCallback(async (
    conversationId: string,
    newName: string,
    {
      onSuccess,
    }: Callback,
  ) => {
    if (conversationRenaming)
      return

    if (!newName.trim()) {
      notify({
        type: 'error',
        message: t('common.chat.conversationNameCanNotEmpty'),
      })
      return
    }

    setConversationRenaming(true)
    try {
      await renameUserConversation(appId, conversationId, newName)

      notify({
        type: 'success',
        message: t('common.actionMsg.modifiedSuccessfully'),
      })
      setOriginConversationList(produce((draft) => {
        const index = originConversationList.findIndex(item => item.id === conversationId)
        const item = draft[index]

        draft[index] = {
          ...item,
          name: newName,
        }
      }))
      onSuccess()
    }
    finally {
      setConversationRenaming(false)
    }
  }, [appId, notify, t, conversationRenaming, originConversationList])

  const handleNewConversationCompleted = useCallback((newConversationId: string) => {
    setNewConversationId(newConversationId)
    handleConversationIdInfoChange(newConversationId)
    setShowNewConversationItemInList(false)
    mutateAppConversationData()
  }, [mutateAppConversationData, handleConversationIdInfoChange])
  const handleFeedback = useCallback(async (messageId: string, feedback: Feedback) => {
    await updateUserFeedback(appId, messageId, { rating: feedback.rating })
    notify({ type: 'success', message: t('common.api.success') })
  }
  , [appId, t, notify])
  // const handleFeedback = useCallback(async (messageId: string, feedback: Feedback) => {
  //   await updateFeedback({ url: `/messages/${messageId}/feedbacks`, body: { rating: feedback.rating } }, isInstalledApp, appId)
  //   notify({ type: 'success', message: t('common.api.success') })
  // }, [isInstalledApp, appId, t, notify])

  return {
    activeIndex,
    setActiveIndex,
    appInfoError,
    appInfoLoading,
    isInstalledApp,
    appId,
    currentConversationId,
    currentConversationItem,
    handleConversationIdInfoChange,
    appData,
    appDataList,
    appParams: appParams || {} as ChatConfig,
    appMeta,
    appPinnedConversationData,
    appConversationData,
    appConversationDataLoading,
    appChatListData,
    appChatListDataLoading,
    appPrevChatList,
    pinnedConversationList,
    conversationList,
    showConfigPanelBeforeChat,
    setShowConfigPanelBeforeChat,
    setShowNewConversationItemInList,
    newConversationInputs,
    newConversationInputsRef,
    handleNewConversationInputsChange,
    inputsForms,
    handleNewConversation,
    handleStartChat,
    handleChangeConversation,
    handlePinConversation,
    handleUnpinConversation,
    conversationDeleting,
    handleDeleteConversation,
    conversationRenaming,
    handleRenameConversation,
    handleNewConversationCompleted,
    newConversationId,
    chatShouldReloadKey,
    handleFeedback,
    currentChatInstanceRef,
  }
}
