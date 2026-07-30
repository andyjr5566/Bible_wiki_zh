import { useState } from 'react'
import { motion } from 'framer-motion'
import { Ruler, Anchor, Info } from 'lucide-react'
import ArkModel3D from '../Canvas/ArkModel3D'
import ScaleToggler from '../UI/ScaleToggler'
import InfoModal from '../UI/InfoModal'

export default function DimensionsSection() {
  const [modalOpen, setModalOpen] = useState(false)

  const specs = [
    { label: '長度', biblical: '300肘', modern: '約137公尺', icon: Ruler },
    { label: '寬度', biblical: '50肘', modern: '約23公尺', icon: Ruler },
    { label: '高度', biblical: '30肘', modern: '約14公尺', icon: Ruler },
    { label: '容積', biblical: '~43,000立方肘', modern: '約40,000立方公尺', icon: Anchor }
  ]

  return (
    <section id="dimensions" className="section-pin wood-texture flex flex-col md:flex-row items-center">
      <div className="w-full md:w-1/2 h-[40vh] md:h-full relative">
        <ArkModel3D autoRotate={true} />
      </div>
      <div className="w-full md:w-1/2 px-8 md:px-16 z-10">
        <motion.h2
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-gold-divine font-serif text-3xl md:text-4xl font-bold mb-2"
        >
          方舟的尺寸
        </motion.h2>
        <p className="text-parchment/50 font-serif text-sm mb-6">創世記 6:15</p>
        <div className="mb-6"><ScaleToggler /></div>
        <div className="grid grid-cols-2 gap-4 mb-6">
          {specs.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="parchment-card rounded-lg p-4"
            >
              <div className="flex items-center gap-2 mb-2 text-wood-primary">
                <s.icon size={16} />
                <span className="font-serif font-bold text-sm">{s.label}</span>
              </div>
              <p className="text-2xl font-serif font-bold text-wood-primary">{s.biblical}</p>
              <p className="text-xs text-wood-primary/60 font-serif mt-1">{s.modern}</p>
            </motion.div>
          ))}
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 text-gold-divine hover:text-parchment transition-colors text-sm font-serif"
        >
          <Info size={16} /> 關於「肘」的換算
        </button>
        <InfoModal open={modalOpen} onClose={() => setModalOpen(false)} title="肘（אמה）的換算">
          <p>一肘約等於45公分（18英吋），是從手肘到中指指尖的距離。<br /><br />
          300肘 ≈ 137公尺，相當於一個半足球場的長度。<br />
          50肘 ≈ 23公尺，約等於一個籃球場的寬度。<br />
          30肘 ≈ 14公尺，約四層樓高。<br /><br />
          方舟的容積約40,000立方公尺，相當於約570節火車貨廂的容量，
          足以容納所有動物物種的代表。</p>
        </InfoModal>
      </div>
    </section>
  )
}
