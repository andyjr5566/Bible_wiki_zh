import { useRef, useEffect, useCallback } from 'react'

export function useAudio(src, volume = 0.3) {
  const soundRef = useRef(null)
  const isReadyRef = useRef(false)

  useEffect(() => {
    let mounted = true
    import('howler').then(({ Howl }) => {
      if (!mounted) return
      soundRef.current = new Howl({ src: [src], volume, loop: true, html5: true })
      isReadyRef.current = true
    })
    return () => {
      mounted = false
      if (soundRef.current) { soundRef.current.unload(); soundRef.current = null }
    }
  }, [src, volume])

  const play = useCallback(() => {
    if (isReadyRef.current && soundRef.current) soundRef.current.fade(0, volume, 2000), soundRef.current.play()
  }, [volume])

  const stop = useCallback(() => {
    if (isReadyRef.current && soundRef.current) soundRef.current.fade(volume, 0, 1500)
  }, [volume])

  return { play, stop }
}
