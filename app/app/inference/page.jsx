import Head from 'next/head'
import Navigation from '@/components/Navigation'
import Inference from '@/components/Inference'

export default function Home() {
  return (
    <div className="w-full flex flex-col items-center">
        <Navigation />
        <Inference />
    </div>
  )
}