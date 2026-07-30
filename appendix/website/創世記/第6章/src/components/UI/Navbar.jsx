import { useState } from 'react'
import { Volume2, VolumeX, BookOpen } from 'lucide-react'
import { useScrollProgress } from '../../hooks/useScrollProgress'

const sections = [
  { id: 'hero', label: '神聖警告' },
  { id: 'dimensions', label: '方舟尺寸' },
  { id: 'construction', label: '建造藍圖' },
  { id: 'boarding', label: '登舟' },
  { id: 'storm', label: '大洪水' },
  { id: 'peace', label: '彩虹之約' }
]

export default function Navbar({ audioOn, onToggleAudio }) {
  const progress = useScrollProgress()
  const [open, setOpen] = useState(false)

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-wood-dark/80 backdrop-blur-md border-b border-gold-divine/20">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-2 text-gold-divine font-serif text-lg font-bold">
            <BookOpen size={20} />
            <span>創世記 第六章</span>
          </div>
          <div className="hidden md:flex gap-6">
            {sections.map(s => (
              <a key={s.id} href={#} className="text-parchment/70 hover:text-gold-divine transition-colors text-sm font-serif">
                {s.label}
              </a>
            ))}
          </div>
          <button onClick={onToggleAudio} className="text-gold-divine hover:text-parchment transition-colors">
            {audioOn ? <Volume2 size={20} /> : <VolumeX size={20} />}
          </button>
        </div>
        <div className="h-0.5 bg-wood-primary">
          <div className="h-full bg-gold-divine transition-all duration-150" style={{ width: ${progress * 100}% }} />
        </div>
      </nav>
    </>
  )
}
