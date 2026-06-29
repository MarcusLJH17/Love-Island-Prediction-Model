import type {
  Contestant,
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

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

function recentSlope(points: { probability: number }[], cursorIndex: number, lookback = 4) {
  const end = points[cursorIndex]?.probability ?? 0;
  const startIndex = Math.max(0, cursorIndex - lookback);
  const start = points[startIndex]?.probability ?? end;
  const days = Math.max(1, cursorIndex - startIndex);
  return (end - start) / days;
}

function volatility(points: { probability: number }[], cursorIndex: number, lookback = 6) {
  const startIndex = Math.max(0, cursorIndex - lookback + 1);
  const values = points.slice(startIndex, cursorIndex + 1).map((point) => point.probability);
  if (values.length < 2) return 0.008;
  const deltas = values.slice(1).map((value, index) => Math.abs(value - values[index]));
  return clamp(deltas.reduce((sum, value) => sum + value, 0) / deltas.length, 0.004, 0.035);
}

function currentFeaturePressure(point: FeaturePoint | undefined) {
  if (!point) return 0;
  const trendPressure = normalizeTrend(point.trends) * 0.012;
  const socialPressure = (point.reddit * 0.009) + (point.twitter * 0.007) + (point.tiktok * 0.006);
  const episodePressure = (point.episode * 0.009) + (point.personal * 0.006) + (point.coupleStatus ? 0.004 : -0.006);
  return clamp(trendPressure + socialPressure + episodePressure, -0.025, 0.03);
}

function contestantRisk(contestant: Contestant, cursorDay: number) {
  if (contestant.exitDay != null && contestant.exitDay <= cursorDay) return -0.08;
  const newcomerDrag = Math.max(0, 5 - (cursorDay - contestant.enteredDay)) * -0.0025;
  const ogStability = contestant.isOG ? 0.004 : 0;
  return newcomerDrag + ogStability;
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

export function makeProjection(
  prediction: ContestantPrediction,
  cursorIndex: number,
  days: number,
  options: { cursorDay: number; season: 7 | 8 }
) {
  const base = prediction.points[cursorIndex]?.probability ?? 0;
  const slope = recentSlope(prediction.points, cursorIndex);
  const movement = volatility(prediction.points, cursorIndex);
  const pressure = currentFeaturePressure(prediction.points[cursorIndex]);
  const risk = contestantRisk(prediction.contestant, options.cursorDay);
  const finalePull = options.season === 8 ? 0.035 : 0.015;
  let value = base;

  return Array.from({ length: days }, (_, idx) => {
    const day = idx + 1;
    const momentumDecay = Math.pow(0.78, day - 1);
    const momentum = slope * 0.9 * momentumDecay;
    const signalCarry = pressure * Math.pow(0.86, day - 1);
    const regression = (0.035 - value) * 0.035;
    const favoriteDurability = base > 0.1 ? finalePull * 0.012 : 0;
    const deterministicShock = Math.sin((prediction.contestant.id.length + day) * 1.31) * movement * 0.22;
    value = clamp(value + momentum + signalCarry + regression + risk + favoriteDurability + deterministicShock, 0.002, 0.7);
    return value;
  });
}
