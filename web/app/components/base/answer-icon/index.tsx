// 修改日期2025-02-28
// 新增text變數輸入文字

'use client'

import type { FC } from 'react'
import { init } from 'emoji-mart'
import data from '@emoji-mart/data'
import classNames from '@/utils/classnames'
import type { AppIconType } from '@/types/app'

init({ data })

export type AnswerIconProps = {
  iconType?: AppIconType | null
  icon?: string | null
  background?: string | null
  imageUrl?: string | null
  text?: string | null
}

const AnswerIcon: FC<AnswerIconProps> = ({
  iconType,
  icon,
  background,
  imageUrl,
  text,
}) => {
  const wrapperClassName = classNames(
    'flex',
    'items-center',
    'justify-center',
    'w-full',
    'h-full',
    'rounded-full',
    'border-[0.5px]',
    'border-black/5',
    'text-xl',
  )
  const isValidImageIcon = iconType === 'image' && imageUrl
  const iconStyle = text
    ? {
      background: background || '#D5F5F6',
      display: text ? 'inline-block' : 'block',
    }
    : { background: background || '#D5F5F6' }
  return <><div
    className={wrapperClassName}
    style={iconStyle}
    // style={{ background: background || '#D5F5F6' }}
  >
    {isValidImageIcon
      ? <img src={imageUrl} className="w-full h-full rounded-full" alt="answer icon" />
      : (icon && icon !== '') ? <em-emoji id={icon} /> : <em-emoji id='🤖' />
    }
  </div>
  {text && <span className="ml-2">{text}</span>}</>
}

export default AnswerIcon
