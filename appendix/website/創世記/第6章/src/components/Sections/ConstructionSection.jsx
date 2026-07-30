import { motion } from 'framer-motion'
import { Hammer, Trees, Layers } from 'lucide-react'

const materials = [
  { icon: Trees, title: '歌斐木', desc: '要用歌斐木造方舟——一種耐腐朽的樹脂木材，適合水上建造。', verse: '6:14' },
  { icon: Layers, title: '三層結構', desc: '方舟分上、中、下三層，內部設有房間，最大化空間利用。', verse: '6:14,16' },
  { icon: Hammer, title: '裡外抹香', desc: '裡外都抹上松香，確保防水——古代造船的標準工序。', verse: '6:14' }
]

export default function ConstructionSection() {
  return (
    <section id="construction" className="section-pin wood-texture flex items-center justify-center">
      <div className="max-w-4xl px-8 z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-gold-divine font-serif text-3xl md:text-4xl font-bold mb-2 text-center"
        >
          建造藍圖
        </motion.h2>
        <p className="text-parchment/50 font-serif text-sm mb-8 text-center">創世記 6:14-16</p>
        <div className="grid md:grid-cols-3 gap-6">
          {materials.map((m, i) => (
            <motion.div
              key={m.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.15 }}
              className="parchment-card rounded-xl p-6 text-center"
            >
              <div className="flex justify-center mb-4">
                <div className="w-14 h-14 rounded-full bg-wood-primary/10 flex items-center justify-center">
                  <m.icon size={28} className="text-wood-primary" />
                </div>
              </div>
              <h3 className="font-serif font-bold text-lg text-wood-primary mb-2">{m.title}</h3>
              <p className="text-sm text-wood-primary/70 font-serif leading-relaxed">{m.desc}</p>
              <p className="text-xs text-gold-divine/60 font-serif mt-3">創 {m.verse}</p>
            </motion.div>
          ))}
        </div>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-8 text-center"
        >
          <p className="text-parchment/60 font-serif text-sm italic">
            「方舟上邊要留透光處，高一肘。方舟的門要開在旁邊。方舟要分上、中、下三層。」
          </p>
          <p className="text-gold-divine/50 font-serif text-xs mt-2">— 創世記 6:16</p>
        </motion.div>
      </div>
    </section>
  )
}
