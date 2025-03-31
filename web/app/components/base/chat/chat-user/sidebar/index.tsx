// 修改日期2025-02-28
// 新增給web-chat介面使用

import {
  useCallback,
  useState,
} from 'react'
import { useTranslation } from 'react-i18next'
import { useRouter } from 'next/navigation'
import {
  RiEditBoxLine,
  RiExpandRightLine,
  RiLayoutLeft2Line,
} from '@remixicon/react'
import { useChatWithHistoryContext } from '../context'
import AppIcon from '@/app/components/base/app-icon'
import ActionButton from '@/app/components/base/action-button'
import Button from '@/app/components/base/button'
import { DotsGrid, LogOut01 } from '@/app/components/base/icons/src/vender/line/general'
import List from '@/app/components/base/chat/chat-with-history/sidebar/list'
import Confirm from '@/app/components/base/confirm'
import RenameModal from '@/app/components/base/chat/chat-with-history/sidebar/rename-modal'
import type { ConversationItem } from '@/models/share'
import Modal from '@/app/components/base/modal'
import { logout } from '@/service/common'
import cn from '@/utils/classnames'

type Props = {
  isPanel?: boolean
}

const Sidebar = ({ isPanel }: Props) => {
  const { t } = useTranslation()
  const router = useRouter()
  const {
    appDataList,
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
    setActiveIndex,
    activeIndex,
    sidebarCollapseState,
    handleSidebarCollapse,
    isMobile,
    isResponding,
  } = useChatWithHistoryContext()
  const isSidebarCollapsed = sidebarCollapseState

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
    setActiveIndex(index)
    setShowApps(false)
  }
  , [setActiveIndex])
  const handleLogout = async () => {
    await logout({
      url: '/logout',
      params: {},
    })

    localStorage.removeItem('setup_status')
    localStorage.removeItem('console_token')
    localStorage.removeItem('refresh_token')

    router.push('/signin')
  }
  return (
    <div className={cn(
      'grow flex flex-col',
      isPanel && 'rounded-xl bg-components-panel-bg border-[0.5px] border-components-panel-border-subtle shadow-lg',
    )}>
      <div className={cn(
        'shrink-0 flex items-center gap-3 p-3 pr-2',
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
        <div className={cn('grow text-text-secondary system-md-semibold truncate')}>{appDataList?.[activeIndex || 0].site.title}</div>
        {!isMobile && isSidebarCollapsed && (
          <ActionButton size='l' onClick={() => handleSidebarCollapse(false)}>
            <RiExpandRightLine className='w-[18px] h-[18px]' />
          </ActionButton>
        )}
        {!isMobile && !isSidebarCollapsed && (
          <ActionButton size='l' onClick={() => handleSidebarCollapse(true)}>
            <RiLayoutLeft2Line className='w-[18px] h-[18px]' />
          </ActionButton>
        )}
      </div>
      <div className='shrink-0 px-3 py-4'>
        <Button
          variant='secondary-accent'
          className='shrink-0 p-4 justify-start w-full'
          onClick={() => setShowApps(true)}
          title='All APPs'>
          <DotsGrid className='mr-2 w-4 h-4' />
          <a>APPs</a>
        </Button>
      </div>
      {(<Modal
        title={'APPs'}
        isShow={showApps}
        onClose={() => setShowApps(false)}
      >
        {appDataList?.length && (
          appDataList.map((appData, index) => (
            <div key={index} className='shrink-0 p-4'>
              <Button
                variant='secondary-accent'
                className='justify-start w-full h-10'
                onClick={() => handleChooseApp(index)}
              >
                <div className='shrink-0 w-10 h-10'>
                  <AppIcon
                    iconType={appData.site.icon_type}
                    icon={appData.site.icon}
                    background={appData.site.icon_background}
                    imageUrl={appData.site.icon_url}
                  />
                </div>
                <div className={cn('grow text-text-secondary system-md-semibold truncate')}>{appData.site.title}</div>
              </Button>
            </div>
          ))
        )}
        <div className='mt-10 flex justify-end'>
          <Button className='mr-2 shrink-0' onClick={() => setShowApps(false)}>{t('common.operation.cancel')}</Button>
        </div>
      </Modal>)}
      <div className='shrink-0 px-3 py-4'>
        <Button variant='secondary-accent' disabled={isResponding} className='w-full justify-center' onClick={handleNewConversation}>
          <RiEditBoxLine className='w-4 h-4 mr-1' />
          {t('share.chat.newChat')}
        </Button>
      </div>
      <div className='grow h-0 pt-4 px-3 space-y-2 overflow-y-auto'>
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
      {(
        <div className='px-4 pb-4 text-xs text-gray-400'>
          <div className='p-1' onClick={() => handleLogout()}>
            <div
              className='flex items-center justify-start h-9 px-3 rounded-lg cursor-pointer group hover:bg-state-base-hover'
            >
              <LogOut01 className='w-4 h-4 text-text-tertiary flex mr-1' />
              <div className='font-normal text-[14px] text-text-secondary'>{t('common.userProfile.logout')}</div>
            </div>
          </div>
        </div>
      )}
      {/* {(<div className='shrink-0 p-3 flex items-center justify-between'>
        <MenuDropdown placement='top-start' data={appDataList?.[activeIndex || 0].site} />
        <div className='shrink-0'>
          {!appDataList?.[activeIndex || 0].custom_config?.remove_webapp_brand && (
            <div className={cn(
              'shrink-0 px-2 flex items-center gap-1.5',
            )}>
              <div className='text-text-tertiary system-2xs-medium-uppercase'>{t('share.chat.poweredBy')}</div>
              {appDataList?.[activeIndex || 0].custom_config?.replace_webapp_logo && (
                <img src={appDataList?.[activeIndex || 0].custom_config?.replace_webapp_logo} alt='logo' className='block w-auto h-5' />
              )}
              {!appDataList?.[activeIndex || 0].custom_config?.replace_webapp_logo && (
                <LogoSite className='!h-5' />
              )}
            </div>
          )}
        </div>
      </div>)} */}
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
