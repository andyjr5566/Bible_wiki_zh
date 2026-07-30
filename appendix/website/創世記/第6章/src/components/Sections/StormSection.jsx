import { motion } from 'framer-motion'
import { CloudRain, Waves } from 'lucide-react'
import RainEffect from '../Canvas/RainEffect'

export default function StormSection() {
  return (
    <section id="storm" className="section-pin relative bg-deluge-dark flex items-center justify-center overflow-hidden">
      <RainEffect intensity={2} />
      <div className="absolute inset-0 bg-gradient-to-b from-deluge-dark via-deluge-mid/40 to-deluge-dark pointer-events-none" />
      <div className="relative z-10 text-center px-8 max-w-3xl">
        <motion.div
          initial={{ scale: 0 }}
          whileInView={{ scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="flex justify-center gap-6 mb-8"
        >
          <CloudRain size={48} className="text-blue-300/60" />
          <Waves size={48} className="text-cyan-300/60" />
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-parchment font-serif text-3xl md:text-5xl font-bold mb-6 text-glow"
        >
          大洪水
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.3 }}
          className="text-parchment/70 font-serif text-lg leading-relaxed mb-6"
        >
          「當挪亞六百歲，二月十七日那一天，大淵的泉源都裂開了，<br />
          天上的窗戶也敞開了，四十晝夜降大雨在地上。」
        </motion.p>
        <p className="text-gold-divine/50 font-serif text-sm mb-8">— 創世記 7:11-12</p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.6 }}
          className="grid grid-cols-3 gap-4 max-w-md mx-auto"
        >
          <div className="text-center">
            <p className="text-3xl font-serif font-bold text-parchment">40</p>
            <p className="text-xs text-parchment/50 font-serif">晝夜大雨</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-serif font-bold text-parchment">150</p>
            <p className="text-xs text-parchment/50 font-serif">日水勢浩大</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-serif font-bold text-parchment">15</p>
            <p className="text-xs text-parchment/50 font-serif">肘高過山嶺</p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
