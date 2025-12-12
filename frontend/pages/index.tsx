/**
 * Grammy Engine Landing Page
 */
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function Home() {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Grammy Engine - AI Music Production Platform</title>
        <meta
          name="description"
          content="Transform your ideas into Grammy-worthy music with AI. The world's first autonomous AI record label."
        />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-grammy-darker via-gray-900 to-grammy-dark">
        {/* Hero Section */}
        <div className="relative overflow-hidden">
          {/* Animated background */}
          <div className="absolute inset-0">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-grammy-purple/20 rounded-full blur-3xl animate-pulse-slow" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-grammy-pink/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
          </div>

          {/* Header */}
          <header className="relative z-10 border-b border-gray-800 bg-black/30 backdrop-blur-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-4xl">🎵</div>
                  <h1 className="text-2xl font-bold bg-gradient-grammy bg-clip-text text-transparent">
                    Grammy Engine
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => router.push('/auth')}
                    className="text-white hover:text-grammy-purple transition"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => router.push('/auth?tab=register')}
                    className="bg-gradient-grammy text-white px-6 py-2 rounded-full font-medium hover:shadow-lg hover:shadow-grammy-purple/50 transition"
                  >
                    Get Started
                  </button>
                </div>
              </div>
            </div>
          </header>

          {/* Hero Content */}
          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32 text-center">
            <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-8">
              <span className="text-grammy-gold">⭐</span>
              <span className="text-sm text-white">
                Powered by AI • MusicGen • GPT-5 • Grammy Meter™
              </span>
            </div>

            <h2 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Turn Your Ideas Into
              <br />
              <span className="bg-gradient-grammy bg-clip-text text-transparent">
                Grammy-Worthy Music
              </span>
            </h2>

            <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
              The world's first autonomous AI record label. Create, mix, master, and distribute professional music in minutes - no musical experience required.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <button
                onClick={() => router.push('/dashboard')}
                className="bg-gradient-grammy text-white px-8 py-4 rounded-full text-lg font-medium hover:shadow-2xl hover:shadow-grammy-purple/50 transition transform hover:scale-105"
              >
                Start Creating Free 🎤
              </button>
              <button
                onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                className="bg-white/10 backdrop-blur text-white px-8 py-4 rounded-full text-lg font-medium hover:bg-white/20 transition"
              >
                See How It Works
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mt-20 max-w-2xl mx-auto">
              {[
                { value: '10M+', label: 'Tracks Generated' },
                { value: '95%', label: 'User Satisfaction' },
                { value: '$2M+', label: 'Royalties Paid' },
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl font-bold bg-gradient-gold bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="py-20 bg-black/30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">
                Complete Music Production Pipeline
              </h2>
              <p className="text-xl text-gray-400">
                From prompt to hit record - fully automated
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: '🎼',
                  title: 'AI Composition',
                  description: 'Generate professional instrumentals from simple text prompts using MusicGen',
                },
                {
                  icon: '🎤',
                  title: 'Vocal Synthesis',
                  description: 'Add AI-generated vocals or clone your own voice with emotion control',
                },
                {
                  icon: '🎚️',
                  title: 'Auto Mix & Master',
                  description: 'Professional-grade mastering to radio standards (-14 LUFS)',
                },
                {
                  icon: '🏆',
                  title: 'Grammy Meter™',
                  description: 'AI-powered hit prediction scoring your commercial potential',
                },
                {
                  icon: '📊',
                  title: 'Trend Analytics',
                  description: 'Real-time insights from Billboard & Spotify chart data',
                },
                {
                  icon: '💰',
                  title: 'Auto Distribution',
                  description: 'One-click upload to Spotify, Apple Music, and NFT marketplaces',
                },
              ].map((feature, i) => (
                <div
                  key={i}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 p-8 rounded-2xl border border-gray-700 hover:border-grammy-purple transition group"
                >
                  <div className="text-5xl mb-4 group-hover:scale-110 transition">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pricing Section */}
        <div className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">
                Simple, Transparent Pricing
              </h2>
              <p className="text-xl text-gray-400">
                Start free, scale as you grow
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  name: 'Starter',
                  price: '$0',
                  period: 'forever',
                  features: [
                    '3 tracks per month',
                    'Basic prompts',
                    'Community support',
                    'Download MP3',
                  ],
                },
                {
                  name: 'Pro Creator',
                  price: '$29',
                  period: 'per month',
                  popular: true,
                  features: [
                    'Unlimited tracks',
                    'AI mastering',
                    'Grammy Score',
                    'Vocal generation',
                    'Priority rendering',
                    'Download WAV',
                    'Commercial license',
                  ],
                },
                {
                  name: 'Label Plan',
                  price: '$199',
                  period: 'per month',
                  features: [
                    'Everything in Pro',
                    'Multi-user seats (5)',
                    'Trend analytics',
                    'Royalty split tools',
                    'API access',
                    'White-label option',
                  ],
                },
              ].map((plan, i) => (
                <div
                  key={i}
                  className={`relative bg-gradient-to-br from-gray-900 to-gray-800 p-8 rounded-2xl border ${
                    plan.popular
                      ? 'border-grammy-purple shadow-xl shadow-grammy-purple/20'
                      : 'border-gray-700'
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-gradient-grammy px-4 py-1 rounded-full text-white text-sm font-medium">
                        Most Popular
                      </span>
                    </div>
                  )}
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {plan.name}
                  </h3>
                  <div className="mb-6">
                    <span className="text-5xl font-bold text-white">
                      {plan.price}
                    </span>
                    <span className="text-gray-400">/{plan.period}</span>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-center text-gray-300">
                        <svg
                          className="w-5 h-5 mr-3 text-grammy-purple"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <button
                    className={`w-full py-3 rounded-full font-medium transition ${
                      plan.popular
                        ? 'bg-gradient-grammy text-white hover:shadow-lg hover:shadow-grammy-purple/50'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    Get Started
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="py-20 bg-gradient-grammy">
          <div className="max-w-4xl mx-auto text-center px-4">
            <h2 className="text-5xl font-bold text-white mb-6">
              Ready to Create Your First Hit?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Join thousands of creators making Grammy-worthy music with AI
            </p>
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-white text-grammy-purple px-8 py-4 rounded-full text-lg font-medium hover:shadow-2xl transform hover:scale-105 transition"
            >
              Start Creating Free →
            </button>
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t border-gray-800 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-400">
            <p>Grammy Engine™ - The World's First Autonomous AI Record Label</p>
            <p className="mt-2 text-sm">
              © 2025 Omni-Tech-Stack. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
