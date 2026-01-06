/**
 * Grammy Engine Dashboard - Main Production Studio
 */
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import PromptInput from '../components/PromptInput';
import AudioVisualizer from '../components/AudioVisualizer';
import MeterGauge from '../components/MeterGauge';
import TrackCard from '../components/TrackCard';
import { useGenerate } from '../hooks/useGenerate';
import { useAuth } from '../hooks/useAuth';
import toast, { Toaster } from 'react-hot-toast';

export default function Dashboard() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const { generate, isGenerating, currentTrack } = useGenerate();
  const [tracks, setTracks] = useState([]);
  const [activeTab, setActiveTab] = useState('generate'); // generate | library | analyze

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth');
    }
  }, [user, loading, router]);

  const handleGenerate = async (prompt: string, options: any) => {
    try {
      const result = await generate(prompt, options);
      toast.success('Track generation started!');
      setActiveTab('library');
    } catch (error: any) {
      toast.error(error.message || 'Generation failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-grammy-darker flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Grammy Engine - AI Music Studio</title>
        <meta name="description" content="Create Grammy-worthy music with AI" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-grammy-darker via-gray-900 to-grammy-dark">
        <Toaster position="top-right" />

        {/* Header */}
        <header className="border-b border-gray-800 bg-black/50 backdrop-blur-lg sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold bg-gradient-grammy bg-clip-text text-transparent">
                  Grammy Engine™
                </h1>
                <span className="text-xs text-gray-400 font-mono">
                  AI Producer of Record
                </span>
              </div>

              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-400">
                  {user?.tier?.toUpperCase() || 'FREE'} TIER
                </div>
                <button
                  onClick={() => router.push('/auth')}
                  className="text-sm text-gray-400 hover:text-white transition"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <div className="flex space-x-4 border-b border-gray-800">
            {[
              { id: 'generate', label: '🎵 Generate', icon: '🎤' },
              { id: 'library', label: '📚 Library', icon: '🎧' },
              { id: 'analyze', label: '🏆 Grammy Meter', icon: '⭐' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-medium transition border-b-2 ${
                  activeTab === tab.id
                    ? 'border-grammy-purple text-white'
                    : 'border-transparent text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'generate' && (
            <div className="space-y-8">
              <div className="bg-gray-900/50 backdrop-blur rounded-2xl p-8 border border-gray-800">
                <h2 className="text-2xl font-bold text-white mb-4">
                  Create Your Hit Song
                </h2>
                <p className="text-gray-400 mb-6">
                  Describe your musical vision and let AI bring it to life
                </p>
                <PromptInput onGenerate={handleGenerate} />
              </div>

              {isGenerating && currentTrack && (
                <div className="bg-gray-900/50 backdrop-blur rounded-2xl p-8 border border-gray-800">
                  <h3 className="text-xl font-bold text-white mb-4">
                    🎨 Generating Your Track...
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Status:</span>
                      <span className="text-grammy-purple font-medium">
                        {currentTrack.status}
                      </span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2">
                      <div
                        className="bg-gradient-grammy h-2 rounded-full transition-all duration-500"
                        style={{ width: `${currentTrack.progress || 0}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <AudioVisualizer />
            </div>
          )}

          {activeTab === 'library' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Your Tracks</h2>
                <div className="flex items-center space-x-4">
                  <select className="bg-gray-900 text-white rounded-lg px-4 py-2 border border-gray-700">
                    <option>All Tracks</option>
                    <option>Completed</option>
                    <option>Generating</option>
                    <option>Failed</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tracks.length === 0 ? (
                  <div className="col-span-full text-center py-12">
                    <p className="text-gray-400 text-lg">
                      No tracks yet. Generate your first hit!
                    </p>
                  </div>
                ) : (
                  tracks.map((track: any) => (
                    <TrackCard key={track.id} track={track} />
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'analyze' && (
            <div className="space-y-6">
              <div className="bg-gray-900/50 backdrop-blur rounded-2xl p-8 border border-gray-800">
                <h2 className="text-2xl font-bold text-white mb-4">
                  Grammy Meter™
                </h2>
                <p className="text-gray-400 mb-6">
                  Analyze your track&apos;s hit potential and commercial readiness
                </p>
                <MeterGauge trackId={currentTrack?.id} />
              </div>

              {/* Leaderboard */}
              <div className="bg-gray-900/50 backdrop-blur rounded-2xl p-8 border border-gray-800">
                <h3 className="text-xl font-bold text-white mb-6">
                  🏆 Top Tracks This Week
                </h3>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((rank) => (
                    <div
                      key={rank}
                      className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <span className="text-2xl font-bold text-grammy-gold">
                          #{rank}
                        </span>
                        <div>
                          <div className="text-white font-medium">
                            Track Title {rank}
                          </div>
                          <div className="text-sm text-gray-400">
                            by User{rank}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-grammy-purple">
                          {95 - rank * 3}
                        </div>
                        <div className="text-xs text-gray-400">Grammy Score</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-400 text-sm">
            <p>
              Grammy Engine™ - The World&apos;s First Autonomous AI Record Label
            </p>
            <p className="mt-2">
              © 2025 Omni-Tech-Stack. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
