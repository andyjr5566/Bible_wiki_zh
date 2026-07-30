import { useRef, useEffect } from 'react'

export default function RainbowCanvas() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId
    let t = 0

    const resize = () => { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight }
    resize()
    window.addEventListener('resize', resize)

    const colors = ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#3498db','#9b59b6','#8e44ad']

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const cx = canvas.width / 2
      const cy = canvas.height * 0.85
      const maxR = Math.min(canvas.width, canvas.height) * 0.7
      const breathe = Math.sin(t * 0.02) * 10

      colors.forEach((color, i) => {
        const r = maxR - i * 18 + breathe
        if (r <= 0) return
        ctx.beginPath()
        ctx.arc(cx, cy, r, Math.PI, Math.PI * 2)
        ctx.strokeStyle = color
        ctx.lineWidth = 16
        ctx.globalAlpha = 0.7 + Math.sin(t * 0.03 + i) * 0.15
        ctx.shadowColor = color
        ctx.shadowBlur = 20
        ctx.stroke()
      })

      ctx.globalAlpha = 1
      ctx.shadowBlur = 0
      t++
      animId = requestAnimationFrame(draw)
    }
    draw()

    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize) }
  }, [])

  return <canvas ref={canvasRef} className="w-full h-full" />
}
