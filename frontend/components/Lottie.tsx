'use client'
import { useEffect, useRef, useState } from 'react'

function hasParentTraversal(path: string): boolean {
  return path.split('/').some((segment) => {
    let decoded = segment

    for (let i = 0; i < 2; i += 1) {
      try {
        const next = decodeURIComponent(decoded)
        if (next === decoded) break
        decoded = next
      } catch {
        return true
      }
    }

    return decoded === '..'
  })
}

function buildValidatedLottieUrl(src: string): string {
  if (!src.startsWith('/') || src.startsWith('//') || src.includes('\\')) {
    throw new Error('Invalid Lottie URL')
  }

  const rawPath = src.split(/[?#]/, 1)[0]
  if (/%(?:2f|5c)/i.test(rawPath) || hasParentTraversal(rawPath)) {
    throw new Error('Invalid Lottie URL')
  }

  const url = new URL(src, window.location.origin)

  if (url.origin !== window.location.origin) {
    throw new Error('Invalid Lottie URL')
  }

  if (!url.pathname.endsWith('.json')) {
    throw new Error('Invalid Lottie URL')
  }

  return url.pathname + url.search
}

/**
 * Thin wrapper around lottie-web that loads a JSON animation from /public.
 * Client-only; renders nothing until the animation is fetched.
 */
export default function Lottie({
  src,
  style,
  loop = true,
}: {
  src: string
  style?: React.CSSProperties
  loop?: boolean
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    let validatedUrl: string
    try {
      validatedUrl = buildValidatedLottieUrl(src)
    } catch {
      console.warn('Blocked invalid Lottie URL:', src)
      return
    }

    let alive = true
    fetch(validatedUrl)
      .then((r) => r.json())
      .then((d) => {
        if (alive) setData(d)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [src])

  useEffect(() => {
    if (!data || !ref.current) return
    let anim: any
    let cancelled = false
    import('lottie-web').then((mod) => {
      if (cancelled || !ref.current) return
      anim = mod.default.loadAnimation({
        container: ref.current,
        renderer: 'svg',
        loop,
        autoplay: true,
        animationData: data,
      })
    })
    return () => {
      cancelled = true
      if (anim) anim.destroy()
    }
  }, [data, loop])

  return <div ref={ref} style={style} aria-hidden />
}
