import { useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import Textarea from '@/app/components/base/textarea'
import { PortalSelect } from '@/app/components/base/select'
import { InputVarType } from '@/app/components/workflow/types'

type Props = {
  inputsForms: any[]
  inputs: Record<string, any>
  inputsRef: any
  onFormChange: (value: Record<string, any>) => void
}
const DatasetInputsForm = ({
  inputsForms,
  inputs,
  inputsRef,
  onFormChange,
}: Props) => {
  const { t } = useTranslation()

  const handleFormChange = useCallback((variable: string, value: any) => {
    onFormChange({
      ...inputsRef.current,
      [variable]: value,
    })
  }, [onFormChange, inputsRef])

  const renderField = (form: any) => {
    const {
      label,
      variable,
      options,
    } = form
    if (form.type === InputVarType.textInput) {
      return (
        <Input
          value={inputs[variable] || ''}
          onChange={e => handleFormChange(variable, e.target.value)}
          placeholder={label}
        />
      )
    }
    if (form.type === InputVarType.number) {
      return (
        <Input
          type="number"
          value={inputs[variable] || ''}
          onChange={e => handleFormChange(variable, e.target.value)}
          placeholder={label}
        />
      )
    }
    if (form.type === InputVarType.paragraph) {
      return (
        <Textarea
          value={inputs[variable] || ''}
          onChange={e => handleFormChange(variable, e.target.value)}
          placeholder={label}
        />
      )
    }
    if (form.type === InputVarType.select) {
      return (
        <PortalSelect
          popupClassName="w-[356px] z-[1050]"
          value={inputs[variable] || ''}
          items={options.map((option: string) => ({ value: option, name: option }))}
          onSelect={item => handleFormChange(variable, item.value as string)}
          placeholder={label}
        />
      )
    }
  }

  if (!inputsForms.length)
    return null

  return (
    <div className='flex flex-col gap-4 px-4 py-2'>
      {inputsForms.map(form => (
        <div key={form.variable}>
          <div className='system-sm-semibold mb-1 flex h-6 items-center gap-1 text-text-secondary'>
            <div className='truncate'>{form.label}</div>
            {!form.required && <span className='system-xs-regular text-text-tertiary'>{t('workflow.panel.optional')}</span>}
          </div>
          {renderField(form)}
        </div>
      ))}
    </div>
  )
}

export default DatasetInputsForm
