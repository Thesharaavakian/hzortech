/**
 * Project intake — a progressive 3-step wizard over the same /api/v1/intake/
 * endpoint the no-JS <form> in contact.html posts to directly. If this
 * island fails to mount, the server-rendered form (one page, one POST) is
 * what the visitor sees and uses — nothing here is load-bearing.
 */
import { useEffect, useRef, useState } from 'react'
import { mountReact } from './shared'
import type { MountFn } from '../core/islands'

type Choice = [string, string]
type Props = {
  initialType: string
  turnstileSiteKey: string
  endpoint: string
  choices: { project_type: Choice[]; budget: Choice[]; timeline: Choice[] }
}

type FormState = {
  project_type: string; message: string; budget: string; timeline: string
  is_urgent: boolean; name: string; email: string; company: string; website: string
}

function getCookie(name: string): string {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : ''
}

function Field({ label, required, hint, children }: { label: string; required?: boolean; hint?: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <label className="field__label">
        {label} <span className={required ? 'field__req' : 'field__opt'}>{required ? 'Required' : 'Optional'}</span>
      </label>
      {hint && <p className="field__hint">{hint}</p>}
      {children}
    </div>
  )
}

function Intake({ initialType, turnstileSiteKey, endpoint, choices }: Props) {
  const [step, setStep] = useState(0)
  const [state, setState] = useState<FormState>({
    project_type: initialType, message: '', budget: '', timeline: '',
    is_urgent: false, name: '', email: '', company: '', website: '',
  })
  const [errors, setErrors] = useState<Record<string, string[]>>({})
  const [sending, setSending] = useState(false)
  const [done, setDone] = useState<{ urgent: boolean } | null>(null)
  const turnstileRef = useRef<HTMLDivElement>(null)
  const tokenRef = useRef<string>('')
  const widgetId = useRef<string>('')

  useEffect(() => {
    if (step !== 2 || !turnstileSiteKey || !turnstileRef.current) return
    const render = () => {
      if (!window.turnstile || widgetId.current) return
      widgetId.current = window.turnstile.render(turnstileRef.current!, {
        sitekey: turnstileSiteKey,
        theme: 'auto',
        callback: (t: string) => { tokenRef.current = t },
      })
    }
    if (window.turnstile) render()
    else {
      const id = window.setInterval(() => { if (window.turnstile) { render(); window.clearInterval(id) } }, 200)
      return () => window.clearInterval(id)
    }
  }, [step, turnstileSiteKey])

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => setState((s) => ({ ...s, [key]: value }))

  const validateStep = (): boolean => {
    const next: Record<string, string[]> = {}
    if (step === 1 && state.message.trim().length < 10) next.message = ['Add a little more detail — at least a sentence helps us reply properly.']
    if (step === 2) {
      if (!state.name.trim()) next.name = ['Please enter your name.']
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email)) next.email = ['That email address doesn’t look right.']
    }
    setErrors((e) => ({ ...e, ...next }))
    return Object.keys(next).length === 0
  }

  const submit = async () => {
    if (state.website) return // honeypot
    if (!validateStep()) return
    setSending(true)
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({ ...state, 'cf-turnstile-response': tokenRef.current }),
      })
      const data = await res.json()
      if (!res.ok || !data.ok) {
        setErrors(data.errors || { __all__: ['Something went wrong — please try again, or email contact@hzortech.com.'] })
        if (data.errors?.name || data.errors?.email) setStep(2)
        else if (data.errors?.message) setStep(1)
        window.turnstile?.reset(widgetId.current)
        tokenRef.current = ''
        return
      }
      setDone({ urgent: !!data.urgent })
    } catch {
      setErrors({ __all__: ['Network error — please try again, or email contact@hzortech.com directly.'] })
    } finally {
      setSending(false)
    }
  }

  if (done) {
    return (
      <div className="intake__success">
        <p className="eyebrow"><span className="eyebrow__index">✓</span> Brief received</p>
        <h2 className="t-h3">Thank you — it’s with an engineer.</h2>
        <p className="t-body">{done.urgent
          ? 'You marked this as urgent, so we’ll triage it today (Mon–Fri, 09:00–18:00 Yerevan time).'
          : 'We reply within 48 hours on working days — with questions or a direct assessment. A confirmation is on its way to your inbox.'}</p>
      </div>
    )
  }

  return (
    <div className="intake">
      <div className="intake__progress" aria-hidden="true">
        {[0, 1, 2].map((i) => <span key={i} className={i <= step ? 'is-done' : ''} />)}
      </div>
      {errors.__all__ && <p className="field__error intake__error-banner" role="alert">{errors.__all__[0]}</p>}

      {step === 0 && (
        <fieldset className="field intake__step">
          <legend className="field__label">What are you working on? <span className="field__opt">Optional</span></legend>
          <div className="choice-grid">
            {choices.project_type.map(([value, label]) => (
              <label className="choice" key={value}>
                <input type="radio" name="project_type" checked={state.project_type === value} onChange={() => set('project_type', value)} />
                <span>{label}</span>
              </label>
            ))}
          </div>
        </fieldset>
      )}

      {step === 1 && (
        <div className="intake__step">
          <Field label="Tell us about it" required hint="What you're trying to achieve, what exists today, and any deadlines. A few lines is fine.">
            <textarea className="textarea" rows={7} value={state.message} onChange={(e) => set('message', e.target.value)}
              aria-invalid={!!errors.message} maxLength={5000} />
            {errors.message && <p className="field__error">{errors.message[0]}</p>}
          </Field>
          <div className="field-row">
            <Field label="Budget"><select className="select input" value={state.budget} onChange={(e) => set('budget', e.target.value)}>
              {choices.budget.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select></Field>
            <Field label="Timeline"><select className="select input" value={state.timeline} onChange={(e) => set('timeline', e.target.value)}>
              {choices.timeline.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select></Field>
          </div>
          <label className="choice" style={{ marginTop: 4 }}>
            <input type="checkbox" checked={state.is_urgent} onChange={(e) => set('is_urgent', e.target.checked)} />
            <span>This is urgent — something is broken in production</span>
          </label>
        </div>
      )}

      {step === 2 && (
        <div className="intake__step">
          <div className="field-row">
            <Field label="Your name" required>
              <input className="input" value={state.name} onChange={(e) => set('name', e.target.value)} autoComplete="name" aria-invalid={!!errors.name} />
              {errors.name && <p className="field__error">{errors.name[0]}</p>}
            </Field>
            <Field label="Email" required>
              <input className="input" type="email" value={state.email} onChange={(e) => set('email', e.target.value)} autoComplete="email" aria-invalid={!!errors.email} />
              {errors.email && <p className="field__error">{errors.email[0]}</p>}
            </Field>
          </div>
          <Field label="Company"><input className="input" value={state.company} onChange={(e) => set('company', e.target.value)} autoComplete="organization" /></Field>
          <div className="visually-hidden" aria-hidden="true"><input tabIndex={-1} autoComplete="off" value={state.website} onChange={(e) => set('website', e.target.value)} /></div>
          {turnstileSiteKey && <div ref={turnstileRef} />}
        </div>
      )}

      <div className="intake__nav">
        {step > 0 ? <button type="button" className="btn" onClick={() => setStep((s) => s - 1)}>Back</button> : <span />}
        {step < 2 ? (
          <button type="button" className="btn btn--primary" onClick={() => { if (validateStep()) setStep((s) => s + 1) }}>
            Continue <svg className="btn__arrow" aria-hidden="true"><use href="#i-arrow" /></svg>
          </button>
        ) : (
          <button type="button" className="btn btn--primary btn--large" disabled={sending} aria-disabled={sending} onClick={submit}>
            {sending ? 'Sending…' : 'Send the brief'} <svg className="btn__arrow" aria-hidden="true"><use href="#i-arrow" /></svg>
          </button>
        )}
      </div>
    </div>
  )
}

export const mount: MountFn = (el, props) => mountReact(el, <Intake {...(props as unknown as Props)} />)
