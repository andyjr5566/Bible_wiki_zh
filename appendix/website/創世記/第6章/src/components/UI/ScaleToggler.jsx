import { useState } from 'react'
import { Ruler, Anchor } from 'lucide-react'

export default function ScaleToggler() {
  const [mode, setMode] = useState('biblical')

  return (
    <div className="flex gap-2 bg-wood-dark/60 rounded-lg p-1 border border-gold-divine/30">
      <button
        onClick={() => setMode('biblical')}
        className={lex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-serif transition-all }
      >
        <Ruler size={14} /> 聖經尺寸
      </button>
      <button
        onClick={() => setMode('modern')}
        className={lex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-serif transition-all }
      >
        <Anchor size={14} /> 現代對比
      </button>
    </div>
  )
}
