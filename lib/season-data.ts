import type { SeasonDataset } from "./types";

const palette = [
  "#D85A30",
  "#2B8C83",
  "#E8B342",
  "#6D5BD0",
  "#D94D8C",
  "#1F7ACB",
  "#7B8E3E",
  "#C3532F",
  "#4062BB",
  "#8D5A97",
  "#008F7A",
  "#B54E62",
  "#4B6C8C",
  "#CF7D1C",
  "#5B7F57",
  "#9B5DE5"
];

function contestant(id: string, name: string, index: number, enteredDay = 1, status: SeasonDataset["contestants"][number]["status"] = "active") {
  return { id, name, color: palette[index % palette.length], isOG: enteredDay === 1, enteredDay, status };
}

function wave(day: number, seed: number, tilt = 0) {
  return Math.max(-1, Math.min(1, Math.sin((day + seed) / 3.1) * 0.38 + Math.cos((day + seed) / 5.3) * 0.24 + tilt));
}

function points(days: number, seed: number, boosts: Partial<Record<number, number>> = {}) {
  return Array.from({ length: days }, (_, idx) => {
    const day = idx + 1;
    const eventBoost = boosts[day] ?? 0;
    const base = wave(day, seed, eventBoost);
    return {
      day,
      reddit: base + wave(day, seed + 5) * 0.25,
      twitter: base * 0.7 + wave(day, seed + 11) * 0.28,
      trends: Math.max(0, Math.min(100, 48 + base * 30 + eventBoost * 18)),
      tiktok: base * 0.8 + wave(day, seed + 17) * 0.2,
      episode: base * 0.45 + eventBoost * 0.55,
      personal: base * 0.35 + eventBoost * 0.5,
      coupleStatus: base + eventBoost > -0.35 ? 1 : 0,
      editVolume: Math.max(1, Math.min(5, Math.round(3 + base * 1.5 + eventBoost)))
    };
  });
}

export const season8: SeasonDataset = {
  season: 8,
  label: "Season 8 Live",
  startDate: "2026-06-02",
  finalDate: "2026-07-12",
  currentDay: 28,
  contestants: [
    contestant("s8-aniya", "Aniya Harvey", 0),
    contestant("s8-kenzie", "Kenzie Annis", 1),
    contestant("s8-bryce", "Bryce Dettloff", 2),
    contestant("s8-kc", "KC Chandler", 3),
    contestant("s8-kayda", "Kayda", 4),
    contestant("s8-zach", "Zach", 5),
    contestant("s8-trinity", "Trinity", 6),
    contestant("s8-melanie", "Melanie", 7),
    contestant("s8-sincere", "Sincere", 8),
    contestant("s8-corbin", "Corbin", 9),
    contestant("s8-caleb", "Caleb", 10),
    contestant("s8-jennifer", "Jennifer", 11),
    contestant("s8-amora", "Amora Cachee", 12, 20),
    contestant("s8-alannah", "Alannah Keyser", 13, 20),
    contestant("s8-jaiden", "Jaiden Bacciocco", 14, 20),
    contestant("s8-tierra", "Tierra Davis", 15, 20)
  ],
  series: []
};

season8.series = season8.contestants.map((c, index) => ({
  contestantId: c.id,
  points: points(season8.currentDay, index * 4 + 1, {
    7: index % 3 === 0 ? 0.35 : 0,
    14: index % 4 === 1 ? 0.42 : -0.08,
    21: index % 5 === 2 ? 0.5 : 0,
    26: c.id === "s8-aniya" || c.id === "s8-kenzie" ? 0.65 : 0
  })
}));

export const season7: SeasonDataset = {
  season: 7,
  label: "Season 7 Backtest",
  startDate: "2025-06-03",
  finalDate: "2025-07-13",
  currentDay: 32,
  contestants: [
    contestant("s7-amaya", "Amaya Espinal", 0, 5, "winner"),
    contestant("s7-bryan", "Bryan Arenales", 1, 10, "winner"),
    contestant("s7-oclandria", "Olandria Carthen", 2, 1, "runner-up"),
    contestant("s7-nic", "Nic Vansteenberghe", 3, 1, "runner-up"),
    contestant("s7-huda", "Huda Mustafa", 4, 1, "runner-up"),
    contestant("s7-chris", "Chris Seeley", 5, 12, "runner-up"),
    contestant("s7-chelley", "Chelley Bissainthe", 6, 1, "runner-up"),
    contestant("s7-ace", "Ace Greene", 7, 1, "runner-up"),
    contestant("s7-taylor", "Taylor Williams", 8, 1, "dumped"),
    contestant("s7-cierra", "Cierra Ortega", 9, 1, "dumped")
  ],
  series: [],
  outcomes: {
    winners: ["s7-amaya", "s7-bryan"],
    finalists: ["s7-amaya", "s7-bryan", "s7-oclandria", "s7-nic", "s7-huda", "s7-chris", "s7-chelley", "s7-ace"],
    dumped: ["s7-taylor", "s7-cierra"]
  }
};

season7.series = season7.contestants.map((c, index) => {
  const winnerTilt = season7.outcomes?.winners.includes(c.id) ? 0.35 : 0;
  const dumpedTilt = season7.outcomes?.dumped.includes(c.id) ? -0.35 : 0;
  return {
    contestantId: c.id,
    points: points(season7.currentDay, index * 5 + 2, {
      9: winnerTilt,
      17: winnerTilt * 1.4 + dumpedTilt,
      25: winnerTilt * 1.8 + dumpedTilt * 1.2,
      31: winnerTilt * 2.2 + dumpedTilt * 1.5
    })
  };
});

export const datasets = [season8, season7];
