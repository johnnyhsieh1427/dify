// 修改日期2025-02-28
// 新增給web-chat介面使用

// 修改日期2025-07-23
// 更新符合最新的ChatWithHistoryContextValue定義

import {
  useCallback,
  useState,
} from 'react'
import { useTranslation } from 'react-i18next'
import {
  RiEditBoxLine,
  RiExpandRightLine,
  RiLayoutLeft2Line,
} from '@remixicon/react'
import { useRouter } from 'next/navigation'
import { useChatWithHistoryContext } from '../context'
import AppIcon from '@/app/components/base/app-icon'
import ActionButton from '@/app/components/base/action-button'
import Button from '@/app/components/base/button'
import List from '@/app/components/base/chat/chat-with-history/sidebar/list'
import MenuDropdown from '@/app/components/share/text-generation/menu-dropdown'
import Confirm from '@/app/components/base/confirm'
import RenameModal from '@/app/components/base/chat/chat-with-history/sidebar/rename-modal'
import DifyLogo from '@/app/components/base/logo/dify-logo'
import type { ConversationItem } from '@/models/share'
import cn from '@/utils/classnames'
import { useWebAppStore } from '@/context/web-app-context'
import { CONVERSATION_ID_INFO } from '../../constants'
import { logout } from '@/service/common'
import Modal from '../../../modal'
import AnswerIcon from '../../../answer-icon'
import { DotsGrid, LogOut01 } from '../../../icons/src/vender/line/general'

type Props = {
  isPanel?: boolean
}

const Sidebar = ({ isPanel }: Props) => {
  const { t } = useTranslation()
  const router = useRouter()
  const {
    handleNewConversation,
    pinnedConversationList,
    conversationList,
    currentConversationId,
    handleChangeConversation,
    handlePinConversation,
    handleUnpinConversation,
    conversationRenaming,
    handleRenameConversation,
    handleDeleteConversation,
    sidebarCollapseState,
    handleSidebarCollapse,
    isMobile,
    isResponding,
    activeIndex,
  } = useChatWithHistoryContext()
  const isSidebarCollapsed = sidebarCollapseState
  const appDataList = useWebAppStore(s => s.appInfoList)
  const setCurrentActiveIndex = useWebAppStore(s => s.setActiveIndex)
  const [showConfirm, setShowConfirm] = useState<ConversationItem | null>(null)
  const [showRename, setShowRename] = useState<ConversationItem | null>(null)
  const [showApps, setShowApps] = useState<boolean>(false)

  const handleOperate = useCallback((type: string, item: ConversationItem) => {
    if (type === 'pin')
      handlePinConversation(item.id)

    if (type === 'unpin')
      handleUnpinConversation(item.id)

    if (type === 'delete')
      setShowConfirm(item)

    if (type === 'rename')
      setShowRename(item)
  }, [handlePinConversation, handleUnpinConversation])
  const handleCancelConfirm = useCallback(() => {
    setShowConfirm(null)
  }, [])
  const handleDelete = useCallback(() => {
    if (showConfirm)
      handleDeleteConversation(showConfirm.id, { onSuccess: handleCancelConfirm })
  }, [showConfirm, handleDeleteConversation, handleCancelConfirm])
  const handleCancelRename = useCallback(() => {
    setShowRename(null)
  }, [])
  const handleRename = useCallback((newName: string) => {
    if (showRename)
      handleRenameConversation(showRename.id, newName, { onSuccess: handleCancelRename })
  }, [showRename, handleRenameConversation, handleCancelRename])
  const handleChooseApp = useCallback((index: number) => {
    setCurrentActiveIndex(index)
    setShowApps(false)
  }, [setCurrentActiveIndex])
  const handleLogout = async () => {
    await logout({ url: '/logout', params: {} })
    localStorage.removeItem('setup_status')
    localStorage.removeItem('token')
    localStorage.removeItem('console_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem(CONVERSATION_ID_INFO)
    router.push('/signin')
  }
  return (
    <div className={cn(
      'flex w-full grow flex-col',
      isPanel && 'rounded-xl border-[0.5px] border-components-panel-border-subtle bg-components-panel-bg shadow-lg',
    )}>
      <div className={cn(
        'flex shrink-0 items-center gap-3 p-3 pr-2',
      )}>
        <div className='shrink-0'>
          <AppIcon
            size='large'
            iconType={appDataList?.[activeIndex || 0].site.icon_type}
            icon={appDataList?.[activeIndex || 0].site.icon}
            background={appDataList?.[activeIndex || 0].site.icon_background}
            imageUrl={appDataList?.[activeIndex || 0].site.icon_url}
          />
        </div>
        <div className={cn('system-md-semibold grow truncate text-text-secondary')}>{appDataList?.[activeIndex || 0].site.title}</div>
        {!isMobile && isSidebarCollapsed && (
          <ActionButton size='l' onClick={() => handleSidebarCollapse(false)}>
            <RiExpandRightLine className='h-[18px] w-[18px]' />
          </ActionButton>
        )}
        {!isMobile && !isSidebarCollapsed && (
          <ActionButton size='l' onClick={() => handleSidebarCollapse(true)}>
            <RiLayoutLeft2Line className='h-[18px] w-[18px]' />
          </ActionButton>
        )}
      </div>
      <div className='shrink-0 px-3 py-4'>
        <Button variant='secondary-accent' disabled={isResponding} className='w-full justify-start' onClick={() => setShowApps(true)}>
          <DotsGrid className='mr-2 h-4 w-4' />
          <a>APPs</a>
        </Button>
      </div>
      {<Modal
        title={'APPs'}
        isShow={showApps}
        onClose={() => setShowApps(false)}
      >
        {appDataList?.length && (
          appDataList.map((appData, index) => (
            <div key={index} className='shrink-0 p-4'>
              <Button
                variant='secondary-accent'
                className='h-10 w-full justify-start'
                onClick={() => handleChooseApp(index)}
              >
                <div className='h-10 w-10 shrink-0'>
                  <AnswerIcon
                    iconType={appData.site.icon_type}
                    icon={appData.site.icon}
                    background={appData.site.icon_background}
                    imageUrl={appData.site.icon_url}
                    text={appData.site.title}
                  />
                </div>
              </Button>
            </div>
          ))
        )}
        <div className='mt-10 flex justify-end'>
          <Button className='mr-2 shrink-0' onClick={() => setShowApps(false)}>{t('common.operation.cancel')}</Button>
        </div>
      </Modal>}
      <div className='shrink-0 px-3 py-4'>
        <Button variant='secondary-accent' disabled={isResponding} className='w-full justify-center' onClick={handleNewConversation}>
          <RiEditBoxLine className='mr-1 h-4 w-4' />
          {t('share.chat.newChat')}
        </Button>
      </div>
      <div className='h-0 grow space-y-2 overflow-y-auto px-3 pt-4'>
        {/* pinned list */}
        {!!pinnedConversationList.length && (
          <div className='mb-4'>
            <List
              isPin
              title={t('share.chat.pinnedTitle') || ''}
              list={pinnedConversationList}
              onChangeConversation={handleChangeConversation}
              onOperate={handleOperate}
              currentConversationId={currentConversationId}
            />
          </div>
        )}
        {!!conversationList.length && (
          <List
            title={(pinnedConversationList.length && t('share.chat.unpinnedTitle')) || ''}
            list={conversationList}
            onChangeConversation={handleChangeConversation}
            onOperate={handleOperate}
            currentConversationId={currentConversationId}
          />
        )}
      </div>
      <div className='px-4 pb-4 text-xs text-gray-400'>
        <div className='p-1' onClick={() => handleLogout()}>
          <div
            className='group flex h-9 cursor-pointer items-center justify-center rounded-lg px-3 hover:bg-state-base-hover'
          >
            <LogOut01 className='mr-1 flex h-4 w-4 text-text-tertiary' />
            <div className='text-[14px] font-normal text-text-secondary'>{t('common.userProfile.logout')}</div>
          </div>
        </div>
      </div>
      <div className='flex shrink-0 items-center justify-between p-3'>
        <MenuDropdown placement='top-start' data={appDataList?.[activeIndex || 0].site} />
        {/* powered by */}
        <div className='shrink-0'>
          {!appDataList?.[activeIndex || 0].custom_config?.remove_webapp_brand && (
            <div className={cn(
              'flex shrink-0 items-center gap-1.5 px-1',
            )}>
              <div className='system-2xs-medium-uppercase text-text-tertiary'>{t('share.chat.poweredBy')}</div>
              {appDataList?.[activeIndex || 0].custom_config?.replace_webapp_logo && (
                <img src={appDataList?.[activeIndex || 0].custom_config?.replace_webapp_logo} alt='logo' className='block h-5 w-auto' />
              )}
              {!appDataList?.[activeIndex || 0].custom_config?.replace_webapp_logo && (
                <DifyLogo size='small' />
              )}
            </div>
          )}
        </div>
      </div>
      {!!showConfirm && (
        <Confirm
          title={t('share.chat.deleteConversation.title')}
          content={t('share.chat.deleteConversation.content') || ''}
          isShow
          onCancel={handleCancelConfirm}
          onConfirm={handleDelete}
        />
      )}
      {showRename && (
        <RenameModal
          isShow
          onClose={handleCancelRename}
          saveLoading={conversationRenaming}
          name={showRename?.name || ''}
          onSave={handleRename}
        />
      )}
    </div>
  )
}

export default Sidebar
