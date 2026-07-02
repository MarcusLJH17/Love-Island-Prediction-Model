export type SignalKey = "reddit" | "twitter" | "trends" | "tiktok" | "episode" | "personal" | "show";

export type Contestant = {
  id: string;
  name: string;
  displayName: string;
  gender: "woman" | "man";
  photoUrl: string;
  color: string;
  isOG: boolean;
  enteredDay: number;
  exitDay?: number;
  status: "active" | "dumped" | "winner" | "runner-up";
};

export type FeaturePoint = {
  day: number;
  reddit: number;
  twitter: number;
  trends: number;
  tiktok: number;
  episode: number;
  personal: number;
  coupleStatus: number;
  editVolume: number;
};

export type ContestantSeries = {
  contestantId: string;
  points: FeaturePoint[];
};

export type SeasonDataset = {
  season: 7 | 8;
  label: string;
  startDate: string;
  finalDate: string;
  currentDay: number;
  contestants: Contestant[];
  series: ContestantSeries[];
  outcomes?: {
    winners: string[];
    finalists: string[];
    dumped: string[];
  };
};

export type ManualTikTokEntry = {
  id: string;
  date: string;
  day?: number;
  contestantId: string;
  positiveSentiment: boolean;
  visibleEditVolume: number;
  commentTone: number;
  viralMomentum: number;
  notes: string;
};

export type ManualEpisodeEntry = {
  id: string;
  date: string;
  day?: number;
  contestantId: string;
  episodeEnjoyment: number;
  gotGoodEdit: boolean;
  relationshipStrength: number;
  riskOfDumping: number;
  notes: string;
};

export type PredictionPoint = FeaturePoint & {
  probability: number;
  score: number;
};

export type ContestantPrediction = {
  contestant: Contestant;
  points: PredictionPoint[];
};
