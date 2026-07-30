import { motion } from 'framer-motion'
import { Bird, Fish, PawPrint } from 'lucide-react'

const animals = [
  { icon: PawPrint, label: '走獸', count: '不潔一對 / 潔淨七對', verse: '7:2' },
  { icon: Bird, label: '飛鳥', count: '不潔一對 / 潔淨七對', verse: '7:3' },
  { icon: Fish, label: '魚類', count: '不在方舟內', verse: '—' }
]

export default function BoardingSection() {
  return (
    <section id="boarding" className="section-pin wood-texture flex items-center">
      <div className="w-full px-8 md:px-16 z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-gold-divine font-serif text-3xl md:text-4xl font-bold mb-2"
        >
          登舟
        </motion.h2>
        <p className="text-parchment/50 font-serif text-sm mb-8">創世記 7:1-5</p>
        <div className="flex flex-col md:flex-row gap-6 items-stretch">
          {animals.map((a, i) => (
            <motion.div
              key={a.label}
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.2 }}
              className="parchment-card rounded-xl p-6 flex-1 flex flex-col items-center"
            >
              <a.icon size={40} className="text-wood-primary mb-3" />
              <h3 className="font-serif font-bold text-lg text-wood-primary">{a.label}</h3>
              <p className="text-sm text-wood-primary/60 font-serif mt-1 text-center">{a.count}</p>
              <p className="text-xs text-gold-divine/60 font-serif mt-2">創 {a.verse}</p>
            </motion.div>
          ))}
        </div>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.8 }}
          className="mt-8 parchment-card rounded-xl p-6"
        >
          <p className="text-wood-primary/80 font-serif leading-relaxed text-sm">
            「挪亞就遵著耶和華所吩咐的行了。」<span className="text-gold-divine/60 text-xs ml-2">— 創 7:5</span>
            <br /><br />
            挪亞六百歲那一年，二月十七日，大淵的泉源裂開，天上的窗戶敞開。
            洪水在地上四十晝夜，水勢浩大，方舟在水面上漂來漂去。
          </p>
        </motion.div>
      </div>
    </section>
  )
}
