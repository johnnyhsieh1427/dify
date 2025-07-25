// 修改日期2025-07-23
// 修改成只能是isCurrentWorkspaceOwner/isCurrentWorkspaceManager才可以進到/apps頁面
// 其他人會被導向/chat-app頁面

'use client'
import { useTranslation } from 'react-i18next'
import { useRouter } from 'next/navigation'
import { RiDiscordFill, RiGithubFill } from '@remixicon/react'
import Link from 'next/link'
import style from '../list.module.css'
import Apps from './Apps'
import { useEducationInit } from '@/app/education-apply/hooks'
import { useAppContext } from '@/context/app-context'
import { useGlobalPublicStore } from '@/context/global-public-context'

const AppList = () => {
  const { t } = useTranslation()
  const { isCurrentWorkspaceOwner, isCurrentWorkspaceManager } = useAppContext()
  const router = useRouter()
  useEducationInit()
  const { systemFeatures } = useGlobalPublicStore()

  if (isCurrentWorkspaceOwner || isCurrentWorkspaceManager) {
    return (
      <div className='relative flex h-0 shrink-0 grow flex-col overflow-y-auto bg-background-body'>
        <Apps />
        {!systemFeatures.branding.enabled && <footer className='shrink-0 grow-0 px-12 py-6'>
          <h3 className='text-gradient text-xl font-semibold leading-tight'>{t('app.join')}</h3>
          <p className='system-sm-regular mt-1 text-text-tertiary'>{t('app.communityIntro')}</p>
          <div className='mt-3 flex items-center gap-2'>
            <Link className={style.socialMediaLink} target='_blank' rel='noopener noreferrer' href='https://github.com/langgenius/dify'>
              <RiGithubFill className='h-5 w-5 text-text-tertiary' />
            </Link>
            <Link className={style.socialMediaLink} target='_blank' rel='noopener noreferrer' href='https://discord.gg/FngNHpbcY7'>
              <RiDiscordFill className='h-5 w-5 text-text-tertiary' />
            </Link>
          </div>
        </footer>}
      </div >
    )
  }
  else {
    router.replace('/chat-app')
  }
}

export default AppList
