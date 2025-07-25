// 修改日期2025-01-20
// 修改內容：
// 增加function fetchAppTenantPermissionc和fetchLoginUser
// 給前端使用function獲取api資料
// 修改日期2025-02-28
// 修改內容：
// 新增function給web-chat使用
import type {
  IOnCompleted,
  IOnData,
  IOnError,
  IOnFile,
  IOnIterationFinished,
  IOnIterationNext,
  IOnIterationStarted,
  IOnLoopFinished,
  IOnLoopNext,
  IOnLoopStarted,
  IOnMessageEnd,
  IOnMessageReplace,
  IOnNodeFinished,
  IOnNodeStarted,
  IOnTTSChunk,
  IOnTTSEnd,
  IOnTextChunk,
  IOnTextReplace,
  IOnThought,
  IOnWorkflowFinished,
  IOnWorkflowStarted,
} from './base'
import {
  del as consoleDel, get as consoleGet, patch as consolePatch, post as consolePost,
  delPublic as del, delWebChat, getPublic as get, getWebChat, patchPublic as patch,
  patchWebChat, postPublic as post, postWebChat, ssePost,
} from './base'
import type { FeedbackType } from '@/app/components/base/chat/chat/type'
import type {
  AppConversationData,
  AppData,
  AppMeta,
  ConversationItem,
} from '@/models/share'
import type { ChatConfig } from '@/app/components/base/chat/types'
import type { AccessMode } from '@/models/access-control'

function getAction(action: 'get' | 'post' | 'del' | 'patch', isInstalledApp: boolean) {
  switch (action) {
    case 'get':
      return isInstalledApp ? consoleGet : get
    case 'post':
      return isInstalledApp ? consolePost : post
    case 'patch':
      return isInstalledApp ? consolePatch : patch
    case 'del':
      return isInstalledApp ? consoleDel : del
  }
}

export function getUrl(url: string, isInstalledApp: boolean, installedAppId: string) {
  if (isInstalledApp) {
    const cleanUrl = url.startsWith('/') ? url.slice(1) : url
    return `installed-apps/${installedAppId}/${cleanUrl}`
  }
  return url
}

export const sendChatMessage = async (body: Record<string, any>, { onData, onCompleted, onThought, onFile, onError, getAbortController, onMessageEnd, onMessageReplace, onTTSChunk, onTTSEnd }: {
  onData: IOnData
  onCompleted: IOnCompleted
  onFile: IOnFile
  onThought: IOnThought
  onError: IOnError
  onMessageEnd?: IOnMessageEnd
  onMessageReplace?: IOnMessageReplace
  getAbortController?: (abortController: AbortController) => void
  onTTSChunk?: IOnTTSChunk
  onTTSEnd?: IOnTTSEnd
}, isInstalledApp: boolean, installedAppId = '') => {
  return ssePost(getUrl('chat-messages', isInstalledApp, installedAppId), {
    body: {
      ...body,
      response_mode: 'streaming',
    },
  }, { onData, onCompleted, onThought, onFile, isPublicAPI: !isInstalledApp, onError, getAbortController, onMessageEnd, onMessageReplace, onTTSChunk, onTTSEnd })
}

export const stopChatMessageResponding = async (appId: string, taskId: string, isInstalledApp: boolean, installedAppId = '') => {
  return getAction('post', isInstalledApp)(getUrl(`chat-messages/${taskId}/stop`, isInstalledApp, installedAppId))
}

export const sendCompletionMessage = async (body: Record<string, any>, { onData, onCompleted, onError, onMessageReplace }: {
  onData: IOnData
  onCompleted: IOnCompleted
  onError: IOnError
  onMessageReplace: IOnMessageReplace
}, isInstalledApp: boolean, installedAppId = '') => {
  return ssePost(getUrl('completion-messages', isInstalledApp, installedAppId), {
    body: {
      ...body,
      response_mode: 'streaming',
    },
  }, { onData, onCompleted, isPublicAPI: !isInstalledApp, onError, onMessageReplace })
}

export const sendWorkflowMessage = async (
  body: Record<string, any>,
  {
    onWorkflowStarted,
    onNodeStarted,
    onNodeFinished,
    onWorkflowFinished,
    onIterationStart,
    onIterationNext,
    onIterationFinish,
    onLoopStart,
    onLoopNext,
    onLoopFinish,
    onTextChunk,
    onTextReplace,
  }: {
    onWorkflowStarted: IOnWorkflowStarted
    onNodeStarted: IOnNodeStarted
    onNodeFinished: IOnNodeFinished
    onWorkflowFinished: IOnWorkflowFinished
    onIterationStart: IOnIterationStarted
    onIterationNext: IOnIterationNext
    onIterationFinish: IOnIterationFinished
    onLoopStart: IOnLoopStarted
    onLoopNext: IOnLoopNext
    onLoopFinish: IOnLoopFinished
    onTextChunk: IOnTextChunk
    onTextReplace: IOnTextReplace
  },
  isInstalledApp: boolean,
  installedAppId = '',
) => {
  return ssePost(getUrl('workflows/run', isInstalledApp, installedAppId), {
    body: {
      ...body,
      response_mode: 'streaming',
    },
  }, {
    onNodeStarted,
    onWorkflowStarted,
    onWorkflowFinished,
    isPublicAPI: !isInstalledApp,
    onNodeFinished,
    onIterationStart,
    onIterationNext,
    onIterationFinish,
    onLoopStart,
    onLoopNext,
    onLoopFinish,
    onTextChunk,
    onTextReplace,
  })
}

export const fetchAppInfo = async () => {
  return get('/site') as Promise<AppData>
}

export const fetchConversations = async (isInstalledApp: boolean, installedAppId = '', last_id?: string, pinned?: boolean, limit?: number) => {
  return getAction('get', isInstalledApp)(getUrl('conversations', isInstalledApp, installedAppId), { params: { ...{ limit: limit || 20 }, ...(last_id ? { last_id } : {}), ...(pinned !== undefined ? { pinned } : {}) } }) as Promise<AppConversationData>
}

export const pinConversation = async (isInstalledApp: boolean, installedAppId = '', id: string) => {
  return getAction('patch', isInstalledApp)(getUrl(`conversations/${id}/pin`, isInstalledApp, installedAppId))
}

export const unpinConversation = async (isInstalledApp: boolean, installedAppId = '', id: string) => {
  return getAction('patch', isInstalledApp)(getUrl(`conversations/${id}/unpin`, isInstalledApp, installedAppId))
}

export const delConversation = async (isInstalledApp: boolean, installedAppId = '', id: string) => {
  return getAction('del', isInstalledApp)(getUrl(`conversations/${id}`, isInstalledApp, installedAppId))
}

export const renameConversation = async (isInstalledApp: boolean, installedAppId = '', id: string, name: string) => {
  return getAction('post', isInstalledApp)(getUrl(`conversations/${id}/name`, isInstalledApp, installedAppId), { body: { name } })
}

export const generationConversationName = async (isInstalledApp: boolean, installedAppId = '', id: string) => {
  return getAction('post', isInstalledApp)(getUrl(`conversations/${id}/name`, isInstalledApp, installedAppId), { body: { auto_generate: true } }) as Promise<ConversationItem>
}

export const fetchChatList = async (conversationId: string, isInstalledApp: boolean, installedAppId = '') => {
  return getAction('get', isInstalledApp)(getUrl('messages', isInstalledApp, installedAppId), { params: { conversation_id: conversationId, limit: 20, last_id: '' } }) as any
}

// Abandoned API interface
// export const fetchAppVariables = async () => {
//   return get(`variables`)
// }

// init value. wait for server update
export const fetchAppParams = async (isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('get', isInstalledApp))(getUrl('parameters', isInstalledApp, installedAppId)) as Promise<ChatConfig>
}

export const fetchWebSAMLSSOUrl = async (appCode: string, redirectUrl: string) => {
  return (getAction('get', false))(getUrl('/enterprise/sso/saml/login', false, ''), {
    params: {
      app_code: appCode,
      redirect_url: redirectUrl,
    },
  }) as Promise<{ url: string }>
}

export const fetchWebOIDCSSOUrl = async (appCode: string, redirectUrl: string) => {
  return (getAction('get', false))(getUrl('/enterprise/sso/oidc/login', false, ''), {
    params: {
      app_code: appCode,
      redirect_url: redirectUrl,
    },

  }) as Promise<{ url: string }>
}

export const fetchWebOAuth2SSOUrl = async (appCode: string, redirectUrl: string) => {
  return (getAction('get', false))(getUrl('/enterprise/sso/oauth2/login', false, ''), {
    params: {
      app_code: appCode,
      redirect_url: redirectUrl,
    },
  }) as Promise<{ url: string }>
}

export const fetchMembersSAMLSSOUrl = async (appCode: string, redirectUrl: string) => {
  return (getAction('get', false))(getUrl('/enterprise/sso/members/saml/login', false, ''), {
    params: {
      app_code: appCode,
      redirect_url: redirectUrl,
    },
  }) as Promise<{ url: string }>
}

export const fetchMembersOIDCSSOUrl = async (appCode: string, redirectUrl: string) => {
  return (getAction('get', false))(getUrl('/enterprise/sso/members/oidc/login', false, ''), {
    params: {
      app_code: appCode,
      redirect_url: redirectUrl,
    },

  }) as Promise<{ url: string }>
}

export const fetchMembersOAuth2SSOUrl = async (appCode: string, redirectUrl: string) => {
  return (getAction('get', false))(getUrl('/enterprise/sso/members/oauth2/login', false, ''), {
    params: {
      app_code: appCode,
      redirect_url: redirectUrl,
    },
  }) as Promise<{ url: string }>
}

export const fetchAppMeta = async (isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('get', isInstalledApp))(getUrl('meta', isInstalledApp, installedAppId)) as Promise<AppMeta>
}

export const updateFeedback = async ({ url, body }: { url: string; body: FeedbackType }, isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('post', isInstalledApp))(getUrl(url, isInstalledApp, installedAppId), { body })
}

export const fetchMoreLikeThis = async (messageId: string, isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('get', isInstalledApp))(getUrl(`/messages/${messageId}/more-like-this`, isInstalledApp, installedAppId), {
    params: {
      response_mode: 'blocking',
    },
  })
}

export const saveMessage = (messageId: string, isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('post', isInstalledApp))(getUrl('/saved-messages', isInstalledApp, installedAppId), { body: { message_id: messageId } })
}

export const fetchSavedMessage = async (isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('get', isInstalledApp))(getUrl('/saved-messages', isInstalledApp, installedAppId))
}

export const removeMessage = (messageId: string, isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('del', isInstalledApp))(getUrl(`/saved-messages/${messageId}`, isInstalledApp, installedAppId))
}

export const fetchSuggestedQuestions = (messageId: string, isInstalledApp: boolean, installedAppId = '') => {
  return (getAction('get', isInstalledApp))(getUrl(`/messages/${messageId}/suggested-questions`, isInstalledApp, installedAppId))
}

export const audioToText = (url: string, isPublicAPI: boolean, body: FormData) => {
  return (getAction('post', !isPublicAPI))(url, { body }, { bodyStringify: false, deleteContentType: true }) as Promise<{ text: string }>
}

export const textToAudio = (url: string, isPublicAPI: boolean, body: FormData) => {
  return (getAction('post', !isPublicAPI))(url, { body }, { bodyStringify: false, deleteContentType: true }) as Promise<{ data: string }>
}

export const textToAudioStream = (url: string, isPublicAPI: boolean, header: { content_type: string }, body: { streaming: boolean; voice?: string; message_id?: string; text?: string | null | undefined }) => {
  return (getAction('post', !isPublicAPI))(url, { body, header }, { needAllResponseContent: true })
}

export const fetchAccessToken = async ({ appCode, userId, webAppAccessToken }: { appCode: string, userId?: string, webAppAccessToken?: string | null }) => {
  const headers = new Headers()
  headers.append('X-App-Code', appCode)
  const params = new URLSearchParams()
  webAppAccessToken && params.append('web_app_access_token', webAppAccessToken)
  userId && params.append('user_id', userId)
  const url = `/passport?${params.toString()}`
  return get(url, { headers }) as Promise<{ access_token: string }>
}

export const getAppAccessMode = (appId: string, isInstalledApp: boolean) => {
  if (isInstalledApp)
    return consoleGet<{ accessMode: AccessMode }>(`/enterprise/webapp/app/access-mode?appId=${appId}`)

  return get<{ accessMode: AccessMode }>(`/webapp/access-mode?appId=${appId}`)
}

export const getUserCanAccess = (appId: string, isInstalledApp: boolean) => {
  if (isInstalledApp)
    return consoleGet<{ result: boolean }>(`/enterprise/webapp/permission?appId=${appId}`)

  return get<{ result: boolean }>(`/webapp/permission?appId=${appId}`)
}

export const fetchLoginUser = async (params: Record<string, any>) => {
  return consoleGet('/passport_auth', { params }) as Promise<{ access_token: string }>
}

export const fetchUserApp = async () => {
  return consoleGet('/passport_user') as Promise<{ access_token: string }>
}

export const fetchAppTenantPermission = async () => {
  return get('/permission') as Promise<{ result: string }>
}

// web-chat controller
// Location: web.controller.web_user.*

export const fetchUserAppInfo = async () => {
  return getWebChat('site') as Promise<{ items: AppData[] }>
}

export const fetchUserAppMeta = async () => {
  return getWebChat('meta') as Promise<AppMeta[]>
}

export const fetchUserAppParams = async () => {
  return getWebChat('parameters') as Promise<ChatConfig[]>
}

export const fetchUserConversations = async (appId: string, last_id?: string, pinned?: boolean, limit?: number) => {
  return getWebChat(`conversations/${appId}`, { params: { ...{ limit: limit || 20 }, ...(last_id ? { last_id } : {}), ...(pinned !== undefined ? { pinned } : {}) } }) as Promise<AppConversationData>
}

export const pinUserConversation = async (appId: string, id: string) => {
  return patchWebChat(`conversations/${appId}/${id}/pin`)
}

export const unpinUserConversation = async (appId: string, id: string) => {
  return patchWebChat(`conversations/${appId}/${id}/unpin`)
}

export const delUserConversation = async (appId: string, id: string) => {
  return delWebChat(`conversations/${appId}/${id}`)
}

export const renameUserConversation = async (appId: string, id: string, name: string) => {
  return postWebChat(`conversations/${appId}/${id}/name`, { body: { name } })
}

export const generationUserConversationName = async (appId: string, id: string) => {
  return postWebChat(`conversations/${appId}/${id}/name`, { body: { auto_generate: true } }) as Promise<ConversationItem>
}

export const fetchUserChatList = async (appId: string, conversationId: string) => {
  return getWebChat(`messages/${appId}`, { params: { conversation_id: conversationId, limit: 20, last_id: '' } }) as any
}

export const updateUserFeedback = async (appId: string, messageId: string, body?: FeedbackType) => {
  return postWebChat(`/messages/${appId}/${messageId}/feedbacks`, { body })
}

export const stopUserChatMessageResponding = async (appId: string, taskId: string) => {
  return postWebChat(`chat-messages/${appId}/${taskId}/stop`)
}

export const getAppAccessModeByAppCode = (appCode: string) => {
  return get<{ accessMode: AccessMode }>(`/webapp/access-mode?appCode=${appCode}`)
}
