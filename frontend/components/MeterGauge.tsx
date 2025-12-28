/**
 * MeterGauge Component - Grammy Meter Score Display
 */
import { useEffect, useState, useCallback } from 'react';
import { api } from '../lib/api';

interface MeterGaugeProps {
  trackId?: string;
}

export default function MeterGauge({ trackId }: MeterGaugeProps) {
  const [score, setScore] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchScore = useCallback(async () => {
    if (!trackId) return;

    setLoading(true);
    try {
      const result = await api.analyzeTrack(trackId);
      setScore(result.overall_score);
      setAnalysis(result);
    } catch (error) {
      console.error('Failed to fetch score:', error);
    } finally {
      setLoading(false);
    }
  }, [trackId]);

  useEffect(() => {
    if (trackId) {
      fetchScore();
    }
  }, [trackId, fetchScore]);

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-yellow-400';
    if (score >= 70) return 'text-green-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 45) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 85) return 'Grammy Worthy';
    if (score >= 70) return 'Hit Potential';
    if (score >= 60) return 'Radio Ready';
    if (score >= 45) return 'Promising';
    return 'Needs Work';
  };

  if (!trackId) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          🏆 Select a track to analyze
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-grammy-purple border-t-transparent mx-auto mb-4"></div>
        <div className="text-gray-400">Analyzing track...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Main Score Gauge */}
      <div className="flex flex-col items-center">
        <div className="relative w-48 h-48 mb-6">
          <svg className="transform -rotate-90 w-48 h-48">
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-gray-800"
            />
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="url(#gradient)"
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${(score || 0) * 5.53} 553`}
              strokeLinecap="round"
              className="transition-all duration-1000"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#8B5CF6" />
                <stop offset="100%" stopColor="#EC4899" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-5xl font-bold ${getScoreColor(score || 0)}`}>
              {score?.toFixed(0) || '—'}
            </div>
            <div className="text-sm text-gray-400 mt-1">Grammy Score</div>
          </div>
        </div>

        <div className="text-center">
          <div className={`text-2xl font-bold ${getScoreColor(score || 0)} mb-2`}>
            {score ? getScoreLabel(score) : '—'}
          </div>
          <div className="text-gray-400">
            Top {score ? Math.max(1, Math.floor((100 - score) * 1.5)) : '—'}% of all tracks
          </div>
        </div>
      </div>

      {/* Category Scores */}
      {analysis?.category_scores && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Category Breakdown</h3>
          {Object.entries(analysis.category_scores).map(([category, value]: [string, any]) => {
            const score = Number(value);
            return (
              <div key={category}>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300 capitalize">
                    {category.replace(/_/g, ' ')}
                  </span>
                  <span className="text-sm font-bold text-white">
                    {score.toFixed(0)}
                  </span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-gradient-grammy h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Insights */}
      {analysis?.insights && analysis.insights.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Key Insights</h3>
          <ul className="space-y-2">
            {analysis.insights.map((insight: string, i: number) => (
              <li key={i} className="flex items-start space-x-2 text-gray-300">
                <span className="text-grammy-purple mt-1">•</span>
                <span className="text-sm">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {analysis?.recommendations && analysis.recommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">
            Recommendations
          </h3>
          <ul className="space-y-2">
            {analysis.recommendations.map((rec: string, i: number) => (
              <li key={i} className="flex items-start space-x-2 text-gray-300">
                <span className="text-yellow-400 mt-1">💡</span>
                <span className="text-sm">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
