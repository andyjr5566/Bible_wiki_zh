import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function InfoModal({ open, onClose, title, children }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="parchment-card rounded-xl max-w-lg w-full mx-4 p-6 relative"
            onClick={e => e.stopPropagation()}
          >
            <button onClick={onClose} className="absolute top-4 right-4 text-wood-primary/60 hover:text-wood-primary">
              <X size={20} />
            </button>
            <h3 className="text-xl font-serif font-bold text-wood-primary mb-3 pr-8">{title}</h3>
            <div className="text-wood-primary/80 font-serif leading-relaxed text-sm">{children}</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
