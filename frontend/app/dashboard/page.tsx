'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Target, Play, User, ArrowLeft } from '@phosphor-icons/react'
import PipelineBoard from '@/components/PipelineBoard'
import ActivityFeed from '@/components/ActivityFeed'
import StatBar from '@/components/StatBar'
import AddCompany from '@/components/AddCompany'
import { getCompanies, getLog, triggerRun } from '@/lib/api'
import type { AgentLog, Company } from '@/lib/api'

async function loadDashboardData() {
  const [companies, logs] = await Promise.all([getCompanies(), getLog()])
  return { companies, logs }
}

export default function Dashboard() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [logs, setLogs] = useState<AgentLog[]>([])
  const [running, setRunning] = useState(false)

  const refresh = async () => {
    const next = await loadDashboardData()
    setCompanies(next.companies)
    setLogs(next.logs)
  }

  useEffect(() => {
    let ignore = false
    const load = () => {
      loadDashboardData().then((next) => {
        if (ignore) return
        setCompanies(next.companies)
        setLogs(next.logs)
      })
    }

    load()
    const interval = setInterval(load, 4000)
    return () => {
      ignore = true
      clearInterval(interval)
    }
  }, [])

  const handleRun = async () => {
    if (running) return
    setRunning(true)
    await triggerRun()
    setTimeout(async () => {
      await refresh()
      setRunning(false)
    }, 1800)
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* ── Header ── */}
      <header
        style={{
          flexShrink: 0,
          zIndex: 20,
          height: 60,
          padding: '0 26px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(250,250,249,0.82)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              color: 'var(--muted)',
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            <ArrowLeft size={15} weight="bold" />
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Target size={18} weight="fill" color="#1c1917" />
            <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em' }}>
              HuntAgent
            </span>
          </div>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              marginLeft: 4,
              padding: '3px 9px',
              borderRadius: 999,
              background: 'var(--surface-2)',
              border: '1px solid var(--border)',
              fontSize: 11,
              color: 'var(--text-dim)',
              fontWeight: 600,
            }}
          >
            <span className="live-dot" />
            Live
          </span>
        </div>

        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <Link
            href="/setup"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              color: 'var(--text-dim)',
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            <User size={15} weight="bold" />
            Profile
          </Link>
          <AddCompany onAdded={refresh} />
          <button onClick={handleRun} disabled={running} className="btn-primary" style={{ padding: '8px 16px', fontSize: 13 }}>
            <Play size={14} weight="fill" />
            {running ? 'Hunting…' : 'Run Hunt'}
          </button>
        </div>
      </header>

      {/* ── Body ── */}
      <main
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) 350px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '26px 28px 60px',
            overflowY: 'auto',
            minHeight: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 22,
          }}
        >
          <StatBar companies={companies} />
          <PipelineBoard
            companies={companies}
            onRun={handleRun}
            running={running}
            onRefresh={refresh}
          />
        </div>

        <aside
          style={{
            borderLeft: '1px solid var(--border)',
            overflowY: 'auto',
            minHeight: 0,
            padding: '24px 20px 60px',
            background: 'var(--surface)',
          }}
        >
          <ActivityFeed logs={logs} running={running} />
        </aside>
      </main>
    </div>
  )
}
