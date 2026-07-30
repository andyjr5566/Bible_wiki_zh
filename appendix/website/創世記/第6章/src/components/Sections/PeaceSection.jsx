import { motion } from 'framer-motion'
import { Dove, Rainbow } from 'lucide-react'
import RainbowCanvas from '../Canvas/RainbowCanvas'

export default function PeaceSection() {
  return (
    <section id="peace" className="section-pin relative wood-texture flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 opacity-40">
        <RainbowCanvas />
      </div>
      <div className="relative z-10 text-center px-8 max-w-3xl">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          whileInView={{ scale: 1, rotate: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1 }}
          className="flex justify-center gap-4 mb-6"
        >
          <Dove size={40} className="text-parchment" />
          <Rainbow size={40} className="text-gold-divine" />
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-gold-divine font-serif text-3xl md:text-5xl font-bold mb-6 text-glow"
        >
          彩虹之約
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.3 }}
          className="text-parchment/80 font-serif text-lg leading-relaxed mb-4"
        >
          「我把虹放在雲彩中，這就可作我與地立約的記號了。<br />
          我使雲彩蓋地的時候，必有虹現在雲彩中。」
        </motion.p>
        <p className="text-gold-divine/50 font-serif text-sm mb-8">— 創世記 9:13-14</p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.6 }}
          className="parchment-card rounded-xl p-6 max-w-xl mx-auto"
        >
          <p className="text-wood-primary/80 font-serif text-sm leading-relaxed">
            洪水之後，挪亞築壇獻祭。神悅納挪亞的祭物，賜福給他和他的兒子，
            又與他們立約：不再用洪水毀滅凡有血肉的活物。
            彩虹成為這永約的記號——神對受造之物的恩典與信實。
          </p>
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.5, delay: 1 }}
          className="text-gold-divine/40 font-serif text-xs mt-8 tracking-widest"
        >
          創世記 第六章 · 挪亞方舟
        </motion.p>
      </div>
    </section>
  )
}
