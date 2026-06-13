'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Check, FloppyDisk } from '@phosphor-icons/react'
import { getProfile, saveProfile } from '@/lib/api'

type FieldKey =
  | 'name'
  | 'role'
  | 'seniority'
  | 'stack'
  | 'location'
  | 'remote_pref'
  | 'dealbreakers'
  | 'bio'
  | 'projects'
  | 'github_url'
  | 'portfolio_url'
  | 'linkedin_url'
  | 'email'
  | 'target_industries'
  | 'target_funding_stages'
  | 'company_size'

export default function SetupPage() {
  const [form, setForm] = useState({
    name: '',
    role: '',
    seniority: '',
    stack: '',
    location: '',
    remote_pref: '',
    dealbreakers: '',
    bio: '',
    projects: '',
    github_url: '',
    portfolio_url: '',
    linkedin_url: '',
    email: '',
    target_industries: '',
    target_funding_stages: '',
    company_size: '',
  })
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getProfile().then((p) => {
      if (p)
        setForm({
          name: p.name || '',
          role: p.role || '',
          seniority: p.seniority || '',
          location: p.location || '',
          remote_pref: p.remote_pref || '',
          bio: p.bio || '',
          projects: p.projects || '',
          github_url: p.github_url || '',
          portfolio_url: p.portfolio_url || '',
          linkedin_url: p.linkedin_url || '',
          email: p.email || '',
          company_size: p.company_size || '',
          stack: (p.stack || []).join(', '),
          dealbreakers: (p.dealbreakers || []).join(', '),
          target_industries: (p.target_industries || []).join(', '),
          target_funding_stages: (p.target_funding_stages || []).join(', '),
        })
    })
  }, [])

  const handleSave = async () => {
    setSaving(true)
    await saveProfile({
      ...form,
      stack: form.stack.split(',').map((s) => s.trim()).filter(Boolean),
      dealbreakers: form.dealbreakers.split(',').map((s) => s.trim()).filter(Boolean),
      target_industries: form.target_industries.split(',').map((s) => s.trim()).filter(Boolean),
      target_funding_stages: form.target_funding_stages
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    })
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2200)
  }

  const field = (
    label: string,
    key: FieldKey,
    opts: { multiline?: boolean; placeholder?: string; hint?: string } = {}
  ) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
      <label
        style={{
          fontSize: 11,
          color: 'var(--text-dim)',
          letterSpacing: '0.07em',
          textTransform: 'uppercase',
          fontWeight: 700,
        }}
      >
        {label}
      </label>
      {opts.multiline ? (
        <textarea
          value={form[key]}
          placeholder={opts.placeholder}
          onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
          rows={4}
          style={inputStyle}
        />
      ) : (
        <input
          value={form[key]}
          placeholder={opts.placeholder}
          onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
          style={inputStyle}
        />
      )}
      {opts.hint && <span style={{ fontSize: 11.5, color: 'var(--muted)' }}>{opts.hint}</span>}
    </div>
  )

  const sectionTitle = (text: string) => (
    <div className="eyebrow" style={{ marginTop: 6 }}>
      {text}
    </div>
  )

  return (
    <div style={{ minHeight: '100vh' }}>
      <div style={{ maxWidth: 680, margin: '0 auto', padding: '40px 24px 90px' }}>
        <Link
          href="/dashboard"
          style={{
            fontSize: 13,
            color: 'var(--text-dim)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            marginBottom: 28,
            fontWeight: 500,
          }}
        >
          <ArrowLeft size={15} weight="bold" />
          Back to dashboard
        </Link>

        <div style={{ marginBottom: 30 }}>
          <h1
            style={{
              fontWeight: 800,
              fontSize: 30,
              letterSpacing: '-0.03em',
              marginBottom: 8,
            }}
          >
            Your profile
          </h1>
          <p style={{ fontSize: 14.5, color: 'var(--text-dim)', maxWidth: 500, lineHeight: 1.6 }}>
            This is what the agents use to find the right companies and write outreach
            that sounds like you, referencing the projects you have actually built. Set
            it once.
          </p>
        </div>

        <div
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px',
            display: 'flex',
            flexDirection: 'column',
            gap: 20,
          }}
        >
          {sectionTitle('Who you are')}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            {field('Name', 'name', { placeholder: 'Bukunmi Oyelekan' })}
            {field('Role', 'role', { placeholder: 'Backend Engineer' })}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            {field('Seniority', 'seniority', { placeholder: 'Senior / Mid / Lead' })}
            {field('Remote preference', 'remote_pref', {
              placeholder: 'Remote / Hybrid / Onsite',
            })}
          </div>

          {field('Stack', 'stack', {
            placeholder: 'Python, FastAPI, Postgres',
            hint: 'Comma-separated. The top 3 drive discovery searches.',
          })}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            {field('Location / preference', 'location', { placeholder: 'Munich / remote EU' })}
            {field('Dealbreakers', 'dealbreakers', {
              placeholder: 'unpaid, internship',
              hint: 'Comma-separated. Filters out bad matches.',
            })}
          </div>

          {field('Bio', 'bio', {
            multiline: true,
            placeholder: 'I build reliable backend systems. Shipped X to N users…',
            hint: 'Lead with what you build. Used as context for outreach.',
          })}

          <div className="hairline" style={{ margin: '4px 0' }} />
          {sectionTitle('What to target')}

          {field('Target industries', 'target_industries', {
            placeholder: 'AI, devtools, fintech, climate',
            hint: 'Comma-separated. The single biggest lever on result quality — be specific.',
          })}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            {field('Funding stages', 'target_funding_stages', {
              placeholder: 'Seed, Series A',
              hint: 'Comma-separated.',
            })}
            {field('Company size', 'company_size', {
              placeholder: '10-200',
              hint: 'Headcount range you want.',
            })}
          </div>

          <div className="hairline" style={{ margin: '4px 0' }} />
          {sectionTitle('What you have built')}

          {field('Projects', 'projects', {
            multiline: true,
            placeholder:
              'Flask Admin Boilerplate — MongoDB + SendGrid + Gunicorn, used by N devs.\nJobNinja — job board scraper and matcher in Python.\n…',
            hint: 'List a few notable projects, one per line. The agent picks the most relevant one to mention per company.',
          })}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            {field('GitHub URL', 'github_url', { placeholder: 'https://github.com/you' })}
            {field('Portfolio URL', 'portfolio_url', { placeholder: 'https://yoursite.com' })}
          </div>

          <div className="hairline" style={{ margin: '4px 0' }} />
          {sectionTitle('How to reach you')}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            {field('LinkedIn URL', 'linkedin_url', { placeholder: 'https://linkedin.com/in/you' })}
            {field('Email', 'email', { placeholder: 'you@example.com' })}
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary"
            style={{ alignSelf: 'flex-start', marginTop: 4 }}
          >
            {saved ? <Check size={16} weight="bold" /> : <FloppyDisk size={16} weight="bold" />}
            {saved ? 'Saved' : saving ? 'Saving…' : 'Save profile'}
          </button>
        </div>
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  borderRadius: 10,
  padding: '11px 13px',
  color: 'var(--text)',
  fontFamily: 'var(--font)',
  fontSize: 14,
  outline: 'none',
  width: '100%',
  resize: 'vertical',
  transition: 'border-color 0.15s',
}
