// 修改日期2025-02-28
// 新增給web-chat介面使用

import {
  useCallback,
  useState,
} from 'react'
import { useTranslation } from 'react-i18next'
import { useRouter } from 'next/navigation'
import { useChatWithHistoryContext } from '../context'
import AnswerIcon from '../../../answer-icon'
import List from './list'
import AppIcon from '@/app/components/base/app-icon'
import Button from '@/app/components/base/button'
import { DotsGrid, Edit05, LogOut01 } from '@/app/components/base/icons/src/vender/line/general'
import type { ConversationItem } from '@/models/share'
import Confirm from '@/app/components/base/confirm'
import RenameModal from '@/app/components/base/chat/chat-with-history/sidebar/rename-modal'
import Modal from '@/app/components/base/modal'
import { logout } from '@/service/common'

const Sidebar = () => {
  const { t } = useTranslation()
  const router = useRouter()
  const {
    appDataList,
    pinnedConversationList,
    conversationList,
    handleNewConversation,
    currentConversationId,
    handleChangeConversation,
    handlePinConversation,
    handleUnpinConversation,
    conversationRenaming,
    handleRenameConversation,
    handleDeleteConversation,
    setActiveIndex,
    activeIndex,
    isMobile,
  } = useChatWithHistoryContext()
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
    <div className='shrink-0 h-full flex flex-col w-[240px] border-r border-r-gray-100'>
      {(<div className='shrink-0 p-4'>
        <Button
          variant='secondary-accent'
          className='shrink-0 p-4 justify-start w-full'
          onClick={() => setShowApps(true)}
          title='All APPs'
        >
          <DotsGrid className='mr-2 w-4 h-4' />
          <a>APPs</a>
        </Button>
      </div>)}
      {(
        <Modal
          title={'APPs'}
          isShow={showApps}
          onClose={() => setShowApps(false)}
        >
          {appDataList?.length && (
            appDataList.map((appData, index) => (
              <div key={index} className='shrink-0 p-4'>
                <Button
                  variant='secondary-accent'
                  // variant={null}
                  className='justify-start w-full h-10'
                  onClick={() => handleChooseApp(index)}
                >
                  {/* <div className='shrink-0 relative w-10 h-10'> */}
                  <div className='shrink-0 w-10 h-10'>
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
            <Button className='mr-2 flex-shrink-0' onClick={() => setShowApps(false)}>{t('common.operation.cancel')}</Button>
          </div>
        </Modal>
      )}
      {
        !isMobile && (
          <div className='shrink-0 flex p-4'>
            <AppIcon
              className='mr-3'
              size='small'
              iconType={appDataList?.[activeIndex || 0].site.icon_type}
              icon={appDataList?.[activeIndex || 0].site.icon}
              background={appDataList?.[activeIndex || 0].site.icon_background}
              imageUrl={appDataList?.[activeIndex || 0].site.icon_url}
            />
            <div className='py-1 text-base font-semibold text-gray-800'>
              {appDataList?.[activeIndex || 0].site.title}
            </div>
          </div>
        )
      }
      <div className='shrink-0 p-4'>
        <Button
          variant='secondary-accent'
          className='justify-start w-full'
          onClick={handleNewConversation}
        >
          <Edit05 className='mr-2 w-4 h-4' />
          {t('share.chat.newChat')}
        </Button>
      </div>
      <div className='grow px-4 py-2 overflow-y-auto'>
        {
          !!pinnedConversationList.length && (
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
          )
        }
        {
          !!conversationList.length && (
            <List
              title={(pinnedConversationList.length && t('share.chat.unpinnedTitle')) || ''}
              list={conversationList}
              onChangeConversation={handleChangeConversation}
              onOperate={handleOperate}
              currentConversationId={currentConversationId}
            />
          )
        }
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
      {/* {appData?.site.copyright && (
        <div className='px-4 pb-4 text-xs text-gray-400'>
          © {(new Date()).getFullYear()} {appData?.site.copyright}
        </div>
      )} */}
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
