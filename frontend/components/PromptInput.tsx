/**
 * PromptInput Component - Main interface for music generation
 */
import { useState } from 'react';
import toast from 'react-hot-toast';

interface PromptInputProps {
  onGenerate: (prompt: string, options: any) => void;
}

export default function PromptInput({ onGenerate }: PromptInputProps) {
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(30);
  const [model, setModel] = useState('musicgen-medium');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleGenerate = () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    onGenerate(prompt, {
      duration,
      model,
    });
  };

  const templates = [
    { id: 'hiphop', label: '🎤 Hip Hop Banger', prompt: 'Hard-hitting hip hop beat, 808 bass, trap influenced, 140 BPM' },
    { id: 'pop', label: '🎵 Pop Hit', prompt: 'Catchy pop track, uplifting melody, radio-ready, 120 BPM' },
    { id: 'edm', label: '🎧 EDM Drop', prompt: 'High-energy EDM, massive drop, festival-ready, 128 BPM' },
    { id: 'lofi', label: '☕ Lo-Fi Chill', prompt: 'Relaxing lo-fi beats, vinyl crackle, study music, 85 BPM' },
  ];

  return (
    <div className="space-y-6">
      {/* Quick Templates */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Quick Start Templates
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {templates.map((template) => (
            <button
              key={template.id}
              onClick={() => setPrompt(template.prompt)}
              className="px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg text-white text-sm transition border border-gray-700 hover:border-grammy-purple"
            >
              {template.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Prompt Input */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Describe Your Track
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="E.g., 'Upbeat summer pop song with tropical vibes, catchy chorus, 120 BPM, perfect for radio'"
          className="w-full h-32 px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-grammy-purple focus:ring-2 focus:ring-grammy-purple/50 transition resize-none"
        />
        <div className="mt-2 text-xs text-gray-400">
          {prompt.length} / 500 characters
        </div>
      </div>

      {/* Basic Settings */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Duration
          </label>
          <select
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:border-grammy-purple transition"
          >
            <option value={15}>15 seconds</option>
            <option value={30}>30 seconds</option>
            <option value={60}>1 minute</option>
            <option value={120}>2 minutes</option>
            <option value={180}>3 minutes</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Model Quality
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:border-grammy-purple transition"
          >
            <option value="musicgen-small">Fast (Small)</option>
            <option value="musicgen-medium">Balanced (Medium)</option>
            <option value="musicgen-large">Best Quality (Large)</option>
          </select>
        </div>
      </div>

      {/* Advanced Settings */}
      <div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-grammy-purple hover:text-grammy-pink transition"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Settings
        </button>

        {showAdvanced && (
          <div className="mt-4 space-y-4 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Temperature (Creativity)
              </label>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.1"
                defaultValue="1.0"
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Conservative</span>
                <span>Experimental</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        className="w-full bg-gradient-grammy text-white px-8 py-4 rounded-xl text-lg font-medium hover:shadow-2xl hover:shadow-grammy-purple/50 transition transform hover:scale-[1.02] active:scale-[0.98]"
      >
        🎵 Generate Track
      </button>

      {/* Info */}
      <div className="text-xs text-gray-400 text-center">
        Generation typically takes 30-120 seconds depending on duration and model
      </div>
    </div>
  );
}
