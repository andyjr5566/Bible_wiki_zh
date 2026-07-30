import { motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

export default function HeroSection() {
  return (
    <section id="hero" className="section-pin wood-texture flex items-center justify-center">
      <div className="text-center z-10 px-6">
        <motion.p
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2 }}
          className="text-gold-divine font-serif text-sm tracking-[0.3em] mb-4"
        >
          創世記 第六章
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.5, delay: 0.3 }}
          className="text-parchment font-serif text-5xl md:text-7xl font-bold text-glow mb-6"
        >
          挪亞方舟
        </motion.h1>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '60%' }}
          transition={{ duration: 1, delay: 1 }}
          className="gold-divider mx-auto mb-6"
        />
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 1.2 }}
          className="text-parchment/70 font-serif text-lg md:text-xl max-w-2xl mx-auto leading-relaxed"
        >
          「神就對挪亞說：凡有血氣的人，他的盡頭已經來到我面前；<br />
          因為地上滿了他們的強暴，我要把他們和地一併毀滅。」
        </motion.p>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 2 }}
          className="text-gold-divine/60 font-serif text-sm mt-4"
        >
          — 創世記 6:13
        </motion.p>
      </div>
      <div className="scroll-hint text-gold-divine/50">
        <ChevronDown size={32} />
      </div>
    </section>
  )
}
