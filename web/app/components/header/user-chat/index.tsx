// 修改日期2025-02-28
// 給web-chat介面使用
'use client'

import { useTranslation } from 'react-i18next'
import Link from 'next/link'
import { useSelectedLayoutSegment } from 'next/navigation'
import {
  RiMessage2Fill,
  RiMessage2Line,
} from '@remixicon/react'
import classNames from '@/utils/classnames'
import type { UserProfileResponse } from '@/models/common'
type UserChatProps = {
  className?: string
  user?: UserProfileResponse
}

const UserChat = ({
  className,
}: UserChatProps) => {
  const { t } = useTranslation()
  const selectedSegment = useSelectedLayoutSegment()
  const activated = selectedSegment === 'user-chat'

  return (
    <Link href={'/chat-app'} className={classNames(
      'group text-sm font-medium',
      activated && 'font-semibold bg-components-main-nav-nav-button-bg-active hover:bg-components-main-nav-nav-button-bg-active-hover shadow-md',
      activated ? 'text-components-main-nav-nav-button-text-active' : 'text-components-main-nav-nav-button-text hover:bg-components-main-nav-nav-button-bg-hover',
      className,
    )}>
      {
        activated
          ? <RiMessage2Fill className='mr-2 w-4 h-4' />
          : <RiMessage2Line className='mr-2 w-4 h-4' />
      }
      {t('common.menus.webChat')}
    </Link>
  )
}

export default UserChat
