import Head from 'next/head'
import Navigation from '@/components/Navigation'
import ModelList from '@/components/ModelList'

export default function Home() {
  return (
    <div className="w-full flex flex-col items-center">
        <Navigation />
        <ModelList />
    </div>
  )
}