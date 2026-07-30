import { useRef, useMemo } from 'react'

export default function RainEffect({ intensity = 1 }) {
  const canvasRef = useRef(null)
  const animRef = useRef(null)
  const dropsRef = useRef([])

  const drops = useMemo(() => {
    const arr = []
    const count = Math.floor(150 * intensity)
    for (let i = 0; i < count; i++) {
      arr.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        len: Math.random() * 20 + 10,
        speed: Math.random() * 8 + 12,
        opacity: Math.random() * 0.3 + 0.1
      })
    }
    return arr
  }, [intensity])

  dropsRef.current = drops

  useMemo(() => {
    if (animRef.current) cancelAnimationFrame(animRef.current)
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.strokeStyle = 'rgba(174, 194, 224, 0.5)'
      ctx.lineWidth = 1
      dropsRef.current.forEach(d => {
        ctx.beginPath()
        ctx.moveTo(d.x, d.y)
        ctx.lineTo(d.x, d.y + d.len)
        ctx.globalAlpha = d.opacity
        ctx.stroke()
        d.y += d.speed
        if (d.y > canvas.height) { d.y = -d.len; d.x = Math.random() * canvas.width }
      })
      animRef.current = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(animRef.current)
  }, [drops])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ width: '100%', height: '100%' }}
    />
  )
}
