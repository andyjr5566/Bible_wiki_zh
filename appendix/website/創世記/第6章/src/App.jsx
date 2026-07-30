import { useState, useEffect, useRef } from 'react'
import { Navbar } from './components/UI/Navbar'
import { InfoModal } from './components/UI/InfoModal'
import { HeroSection } from './components/Sections/HeroSection'
import { DimensionsSection } from './components/Sections/DimensionsSection'
import { ConstructionSection } from './components/Sections/ConstructionSection'
import { BoardingSection } from './components/Sections/BoardingSection'
import { StormSection } from './components/Sections/StormSection'
import { PeaceSection } from './components/Sections/PeaceSection'
import { useScrollProgress } from './hooks/useScrollProgress'
import { useAudio } from './hooks/useAudio'

export default function App() {
  const [modalContent, setModalContent] = useState(null)
  const [audioEnabled, setAudioEnabled] = useState(false)
  const scrollProgress = useScrollProgress()
  const audioRef = useRef(null)

  useEffect(() => {
    if (audioEnabled) {
      audioRef.current = useAudio('/ambient/rain.mp3', 0.3)
      audioRef.current?.play()
    } else {
      audioRef.current?.stop()
    }
  }, [audioEnabled])

  return (
    <div className="relative w-full bg-wood-dark text-parchment font-serif">
      <Navbar
        audioEnabled={audioEnabled}
        onToggleAudio={() => setAudioEnabled(!audioEnabled)}
        scrollProgress={scrollProgress}
      />
      <main>
        <HeroSection onOpenModal={setModalContent} />
        <DimensionsSection onOpenModal={setModalContent} />
        <ConstructionSection onOpenModal={setModalContent} />
        <BoardingSection onOpenModal={setModalContent} />
        <StormSection onOpenModal={setModalContent} />
        <PeaceSection onOpenModal={setModalContent} />
      </main>
      {modalContent && (
        <InfoModal content={modalContent} onClose={() => setModalContent(null)} />
      )}
    </div>
  )
}
