import type {
  ContestantPrediction,
  FeaturePoint,
  ManualEpisodeEntry,
  ManualTikTokEntry,
  SeasonDataset,
  SignalKey
} from "./types";

export const signalLabels: Record<SignalKey, string> = {
  reddit: "Reddit",
  twitter: "Twitter/X",
  trends: "Google Trends",
  tiktok: "TikTok",
  episode: "Episode Data",
  personal: "Personal Notes"
};

export const defaultSignals: Record<SignalKey, boolean> = {
  reddit: true,
  twitter: true,
  trends: true,
  tiktok: true,
  episode: true,
  personal: true
};

const weights: Record<SignalKey, number> = {
  reddit: 0.23,
  twitter: 0.18,
  trends: 0.16,
  tiktok: 0.18,
  episode: 0.15,
  personal: 0.1
};

function sigmoid(value: number) {
  return 1 / (1 + Math.exp(-value));
}

function normalizeTrend(value: number) {
  return (value - 50) / 50;
}

function manualTikTokImpact(entries: ManualTikTokEntry[], contestantId: string) {
  const selected = entries.filter((entry) => entry.contestantId === contestantId);
  if (!selected.length) return 0;
  return selected.reduce((sum, entry) => {
    const polarity = entry.positiveSentiment ? 0.35 : -0.35;
    return sum + polarity + (entry.visibleEditVolume - 3) * 0.11 + (entry.commentTone - 3) * 0.13 + (entry.viralMomentum - 3) * 0.12;
  }, 0) / selected.length;
}

function manualEpisodeImpact(entries: ManualEpisodeEntry[], contestantId: string) {
  const selected = entries.filter((entry) => entry.contestantId === contestantId);
  if (!selected.length) return 0;
  return selected.reduce((sum, entry) => {
    const edit = entry.gotGoodEdit ? 0.25 : -0.12;
    return sum + edit + (entry.episodeEnjoyment - 3) * 0.1 + (entry.relationshipStrength - 3) * 0.16 - (entry.riskOfDumping - 3) * 0.18;
  }, 0) / selected.length;
}

function featureScore(point: FeaturePoint, signals: Record<SignalKey, boolean>, tiktokBoost: number, personalBoost: number) {
  const pieces = {
    reddit: point.reddit,
    twitter: point.twitter,
    trends: normalizeTrend(point.trends),
    tiktok: point.tiktok + tiktokBoost,
    episode: point.episode + point.coupleStatus * 0.12,
    personal: point.personal + personalBoost
  };

  return (Object.keys(weights) as SignalKey[]).reduce((score, key) => {
    return signals[key] ? score + pieces[key] * weights[key] : score;
  }, 0);
}

function normalizeDay(predictions: ContestantPrediction[], pointIndex: number) {
  const raw = predictions.map((prediction) => Math.exp((prediction.points[pointIndex]?.score ?? -1) * 2.8));
  const total = raw.reduce((sum, value) => sum + value, 0);
  predictions.forEach((prediction, index) => {
    if (prediction.points[pointIndex]) {
      prediction.points[pointIndex].probability = raw[index] / total;
    }
  });
}

export function buildPredictions(
  dataset: SeasonDataset,
  signals: Record<SignalKey, boolean>,
  tiktokEntries: ManualTikTokEntry[] = [],
  episodeEntries: ManualEpisodeEntry[] = []
) {
  const predictions = dataset.contestants.map((contestant) => {
    const series = dataset.series.find((item) => item.contestantId === contestant.id);
    const tiktokBoost = manualTikTokImpact(tiktokEntries, contestant.id);
    const personalBoost = manualEpisodeImpact(episodeEntries, contestant.id);
    const points = (series?.points ?? []).map((point, index) => {
      const longevity = Math.min(0.4, index * 0.012);
      const entryPenalty = contestant.enteredDay > point.day ? -1.4 : 0;
      const ogBoost = contestant.isOG ? 0.05 : 0;
      const score = featureScore(point, signals, tiktokBoost, personalBoost) + longevity + entryPenalty + ogBoost;
      return {
        ...point,
        score,
        probability: sigmoid(score)
      };
    });
    return { contestant, points };
  });

  for (let pointIndex = 0; pointIndex < dataset.currentDay; pointIndex += 1) {
    normalizeDay(predictions, pointIndex);
  }

  return predictions;
}

export function makeProjection(lastProbability: number, days: number, seed: number) {
  return Array.from({ length: days }, (_, idx) => {
    const day = idx + 1;
    const uncertainty = Math.sqrt(day) * 0.018;
    const drift = Math.sin((seed + day) * 1.7) * uncertainty;
    return Math.max(0.002, Math.min(0.7, lastProbability + drift));
  });
}
