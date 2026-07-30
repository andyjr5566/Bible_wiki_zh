import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, Float, Text } from '@react-three/drei'
import * as THREE from 'three'

function ArkHull() {
  const ref = useRef()
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.05
      ref.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  const woodMat = useMemo(() => new THREE.MeshStandardMaterial({ color: '#3e2723', roughness: 0.85, metalness: 0.1 }), [])
  const darkWoodMat = useMemo(() => new THREE.MeshStandardMaterial({ color: '#1c130b', roughness: 0.9 }), [])
  const goldMat = useMemo(() => new THREE.MeshStandardMaterial({ color: '#d4af37', roughness: 0.3, metalness: 0.8 }), [])

  return (
    <group ref={ref}>
      {/* Hull base */}
      <mesh material={woodMat} castShadow receiveShadow>
        <boxGeometry args={[3, 0.8, 1]} />
      </mesh>
      {/* Hull bottom taper */}
      <mesh material={darkWoodMat} position={[0, -0.5, 0]} castShadow>
        <boxGeometry args={[2.8, 0.3, 0.8]} />
      </mesh>
      {/* Deck */}
      <mesh material={woodMat} position={[0, 0.5, 0]} castShadow>
        <boxGeometry args={[3.1, 0.05, 1.05]} />
      </mesh>
      {/* Three decks */}
      {[0.15, 0.0, -0.15].map((y, i) => (
        <mesh key={i} material={darkWoodMat} position={[0, y + 0.3, 0]}>
          <boxGeometry args={[2.9, 0.02, 0.95]} />
        </mesh>
      ))}
      {/* Roof / cabin */}
      <mesh material={woodMat} position={[0, 0.85, 0]} castShadow>
        <boxGeometry args={[2.5, 0.5, 0.9]} />
      </mesh>
      {/* Roof slope */}
      <mesh material={darkWoodMat} position={[0, 1.15, 0]} rotation={[0, 0, 0]} castShadow>
        <cylinderGeometry args={[0.45, 0.45, 2.5, 3, 1, false, 0, Math.PI]} />
      </mesh>
      {/* Door */}
      <mesh material={goldMat} position={[1.5, 0.3, 0]}>
        <boxGeometry args={[0.02, 0.5, 0.4]} />
      </mesh>
      {/* Window slits */}
      {[-1, -0.3, 0.4, 1.1].map((x, i) => (
        <mesh key={i} material={goldMat} position={[x, 0.65, 0.48]}>
          <boxGeometry args={[0.3, 0.08, 0.02]} />
        </mesh>
      ))}
    </group>
  )
}

function Scene({ autoRotate }) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={0.8} castShadow />
      <pointLight position={[-5, 3, -5]} intensity={0.3} color="#d4af37" />
      <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>
        <ArkHull />
      </Float>
      <Environment preset="sunset" />
      {autoRotate && <OrbitControls autoRotate autoRotateSpeed={0.5} enableZoom={true} enablePan={false} minPolarAngle={Math.PI / 4} maxPolarAngle={Math.PI / 1.8} />}
    </>
  )
}

export default function ArkModel3D({ autoRotate = true }) {
  return (
    <Canvas shadows camera={{ position: [4, 3, 5], fov: 45 }} dpr={[1, 2]}>
      <Scene autoRotate={autoRotate} />
    </Canvas>
  )
}
