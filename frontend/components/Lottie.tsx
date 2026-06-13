'use client'
import { useEffect, useRef } from 'react'
import type { AnimationItem } from 'lottie-web'

/**
 * Thin wrapper around lottie-web that renders bundled animation data.
 * Client-only; callers import local JSON instead of passing a fetchable URL.
 */
export default function Lottie({
  animationData,
  style,
  loop = true,
}: {
  animationData: unknown
  style?: React.CSSProperties
  loop?: boolean
}) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!animationData || !ref.current) return
    let anim: AnimationItem | null = null
    let cancelled = false
    import('lottie-web').then((mod) => {
      if (cancelled || !ref.current) return
      anim = mod.default.loadAnimation({
        container: ref.current,
        renderer: 'svg',
        loop,
        autoplay: true,
        animationData,
      })
    })
    return () => {
      cancelled = true
      anim?.destroy()
    }
  }, [animationData, loop])

  return <div ref={ref} style={style} aria-hidden />
}
