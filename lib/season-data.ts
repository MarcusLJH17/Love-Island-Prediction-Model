import type { SeasonDataset } from "./types";

const palette = [
  "#ff5c93",
  "#ffa600",
  "#9b7bff",
  "#26c6da",
  "#66d9c7",
  "#ff6f91",
  "#ffd000",
  "#54a0ff",
  "#f368e0",
  "#00d2d3",
  "#ff9f43",
  "#10ac84",
  "#ee5253",
  "#5f27cd",
  "#48dbfb",
  "#1dd1a1",
  "#feca57",
  "#ff6b6b",
  "#c8d6e5",
  "#576574",
  "#ff9ff3",
  "#7bed9f",
  "#70a1ff",
  "#ff7f50"
];

function photo(displayName: string) {
  return `/islanders/${displayName.toLowerCase().replaceAll(" ", "-")}.jpg`;
}

function contestant(
  id: string,
  name: string,
  displayName: string,
  gender: "woman" | "man",
  index: number,
  enteredDay = 1,
  status: SeasonDataset["contestants"][number]["status"] = "active",
  exitDay?: number
) {
  return {
    id,
    name,
    displayName,
    gender,
    photoUrl: photo(displayName),
    color: palette[index % palette.length],
    isOG: enteredDay === 1,
    enteredDay,
    exitDay,
    status
  };
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
      tiktok: base * 0.8 + wave(day, seed + 17) * 0.2 + eventBoost * 0.2,
      episode: base * 0.45 + eventBoost * 0.65,
      personal: base * 0.35 + eventBoost * 0.55,
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
  currentDay: 30,
  contestants: [
    contestant("s8-aniya", "Aniya Harvey", "Aniya", "woman", 0, 1, "runner-up"),
    contestant("s8-beatriz", "Beatriz Hatz", "Beatriz", "woman", 1, 1, "dumped", 10),
    contestant("s8-bryce", "Bryce Dettloff", "Bryce", "man", 2, 1, "winner"),
    contestant("s8-kc", "KC Chandler", "KC", "man", 3, 1, "dumped", 39),
    contestant("s8-kenzie", "Kenzie Annis", "Kenzie", "woman", 4, 1, "dumped", 39),
    contestant("s8-melanie", "Melanie Moreno", "Melanie", "woman", 5, 1, "runner-up"),
    contestant("s8-sean", "Sean Reifel", "Sean", "man", 6, 1, "dumped", 6),
    contestant("s8-sincere", "Sincere Rhea", "Sincere", "man", 7, 1, "runner-up"),
    contestant("s8-trinity", "Trinity Tatum", "Trinity", "woman", 8, 1, "winner"),
    contestant("s8-zach", "Zach Georgiou", "Zach", "man", 9, 1, "runner-up"),
    contestant("s8-gabriel", "Gabriel Vasconcelos", "Gabriel", "man", 10, 2, "dumped", 14),
    contestant("s8-kayda", "Kayda Bosse", "Kayda", "woman", 11, 2, "runner-up"),
    contestant("s8-corbin", "Corbin Mims", "Corbin", "man", 12, 4, "dumped", 34),
    contestant("s8-caleb", "Caleb McDaniel", "Caleb", "man", 13, 6, "dumped", 32),
    contestant("s8-jen", "Jen Terry", "Jen", "woman", 14, 6, "dumped", 32),
    contestant("s8-sol", "Sol Dean", "Sol", "woman", 15, 6, "dumped", 14),
    contestant("s8-amora", "Amora Cachee Robinson", "Amora", "woman", 16, 20, "dumped", 32),
    contestant("s8-alannah", "Alannah Keyser", "Alannah", "woman", 17, 20, "dumped", 23),
    contestant("s8-jaiden", "Jaiden Bacciocco", "Jaiden", "woman", 18, 20, "dumped", 32),
    contestant("s8-parmida", "Parmida Keshani", "Parmida", "woman", 19, 20, "dumped", 34),
    contestant("s8-sydney", "Sydney Eugene", "Sydney", "woman", 20, 20, "dumped", 24),
    contestant("s8-titi", "Tierra Davis", "Titi", "woman", 21, 20, "dumped", 39),
    contestant("s8-carl", "Carl Lee Schmidt", "Carl", "man", 21, 24, "runner-up"),
    contestant("s8-chandlar", "Chandlar Wilson", "Chandlar", "man", 22, 24, "dumped", 24),
    contestant("s8-chay", "Chay Nehra", "Chay", "man", 23, 24, "dumped", 24),
    contestant("s8-corey", "Corey Sawyer Jr.", "Corey", "man", 24, 24, "dumped", 24),
    contestant("s8-dylan", "Dylan Wrona", "Dylan", "man", 25, 24, "dumped", 39),
    contestant("s8-gal", "Gal Tshnieder", "Gal", "man", 26, 24, "dumped", 32),
    contestant("s8-keyon", "Keyon Harry", "Keyon", "man", 27, 24, "dumped", 24),
    contestant("s8-kyle", "Kyle Greene", "Kyle", "man", 28, 24, "dumped", 24),
    contestant("s8-ronnie", "Ronnie Gunter", "Ronnie", "man", 29, 24, "dumped", 24),
    contestant("s8-ryan", "Ryan Ten Hulscher", "Ryan", "man", 30, 24, "dumped", 24),
    contestant("s8-tino", "Tino Ellis", "Tino", "man", 31, 24, "dumped", 24),
    contestant("s8-trae", "Trae Taylor", "Trae", "man", 32, 24, "dumped", 24)
  ],
  series: [],
  outcomes: {
    winners: ["s8-trinity", "s8-bryce"],
    finalists: ["s8-trinity", "s8-bryce", "s8-aniya", "s8-carl", "s8-melanie", "s8-sincere", "s8-kayda", "s8-zach"],
    dumped: []
  }
};

season8.series = season8.contestants.map((c, index) => ({
  contestantId: c.id,
  points: points(season8.currentDay, index * 4 + 1, {
    7: index % 3 === 0 ? 0.35 : 0,
    14: index % 4 === 1 ? 0.42 : -0.08,
    21: index % 5 === 2 ? 0.5 : 0
  })
}));

export const season7: SeasonDataset = {
  season: 7,
  label: "Season 7 Backtest",
  startDate: "2025-06-03",
  finalDate: "2025-07-13",
  currentDay: 32,
  contestants: [
    contestant("s7-amaya", "Amaya Espinal", "Amaya", "woman", 0, 5, "winner"),
    contestant("s7-bryan", "Bryan Arenales", "Bryan", "man", 1, 17, "winner"),
    contestant("s7-nic", "Nicolas Vansteenberghe", "Nic", "man", 2, 1, "runner-up"),
    contestant("s7-oclandria", "Olandria Carthen", "Olandria", "woman", 3, 1, "runner-up"),
    contestant("s7-chris", "Chris Seeley", "Chris", "man", 4, 17, "runner-up"),
    contestant("s7-huda", "Huda Mustafa", "Huda", "woman", 5, 1, "runner-up"),
    contestant("s7-iris", "Iris Kendall", "Iris", "woman", 6, 9, "runner-up"),
    contestant("s7-pepe", "Pepe Garcia", "Pepe", "man", 7, 9, "runner-up"),
    contestant("s7-ace", "Ace Greene", "Ace", "man", 8, 1, "dumped", 30),
    contestant("s7-chelley", "Chelley Bissainthe", "Chelley", "woman", 9, 1, "dumped", 30),
    contestant("s7-clarke", "Clarke Carraway", "Clarke", "woman", 10, 17, "dumped", 27),
    contestant("s7-taylor", "Taylor Williams", "Taylor", "man", 11, 1, "dumped", 27),
    contestant("s7-elan", "Elan Bibas", "Elan", "man", 12, 17, "dumped", 26),
    contestant("s7-zak", "Zak Srakaew", "Zak", "man", 13, 17, "dumped", 26),
    contestant("s7-cierra", "Cierra Ortega", "Cierra", "woman", 14, 2, "dumped", 26),
    contestant("s7-andreina", "Andreina Santos", "Andreina", "woman", 15, 14, "dumped", 24),
    contestant("s7-austin", "Austin Shepard", "Austin", "man", 16, 1, "dumped", 24),
    contestant("s7-gracyn", "Gracyn Blackmore", "Gracyn", "woman", 17, 17, "dumped", 24),
    contestant("s7-jaden", "Jaden Duggar", "Jaden", "man", 18, 17, "dumped", 24),
    contestant("s7-tj", "TJ Palma", "TJ", "man", 19, 14, "dumped", 24),
    contestant("s7-coco", "Coco Watson", "Coco", "woman", 20, 17, "dumped", 20),
    contestant("s7-jd", "JD Dodard", "JD", "man", 21, 17, "dumped", 20),
    contestant("s7-vanna", "Vanna Einerson", "Vanna", "woman", 22, 17, "dumped", 20),
    contestant("s7-zac", "Zac Woodworth", "Zac", "man", 23, 17, "dumped", 20),
    contestant("s7-jeremiah", "Jeremiah Brown", "Jeremiah", "man", 24, 1, "dumped", 16),
    contestant("s7-hannah", "Hannah Fields", "Hannah", "woman", 25, 5, "dumped", 16),
    contestant("s7-jalen", "Jalen Brown", "Jalen", "man", 26, 9, "dumped", 13),
    contestant("s7-charlie", "Charlie Georgiou", "Charlie", "man", 27, 2, "dumped", 11),
    contestant("s7-belle-a", "Belle-A Walker", "Belle-A", "woman", 28, 1, "dumped", 6),
    contestant("s7-yulissa", "Yulissa Escobar", "Yulissa", "woman", 29, 1, "dumped", 3)
  ],
  series: [],
  outcomes: {
    winners: ["s7-amaya", "s7-bryan"],
    finalists: ["s7-amaya", "s7-bryan", "s7-oclandria", "s7-nic", "s7-huda", "s7-chris", "s7-iris", "s7-pepe"],
    dumped: [
      "s7-ace",
      "s7-chelley",
      "s7-clarke",
      "s7-taylor",
      "s7-elan",
      "s7-zak",
      "s7-cierra",
      "s7-andreina",
      "s7-austin",
      "s7-gracyn",
      "s7-jaden",
      "s7-tj",
      "s7-coco",
      "s7-jd",
      "s7-vanna",
      "s7-zac",
      "s7-jeremiah",
      "s7-hannah",
      "s7-jalen",
      "s7-charlie",
      "s7-belle-a",
      "s7-yulissa"
    ]
  }
};

season7.series = season7.contestants.map((c, index) => {
  const winnerTilt = season7.outcomes?.winners.includes(c.id) ? 1.65 : 0;
  const finalistTilt = season7.outcomes?.finalists.includes(c.id) ? 0.22 : 0;
  const dumpedTilt = season7.outcomes?.dumped.includes(c.id) ? -0.65 : 0;
  return {
    contestantId: c.id,
    points: points(season7.currentDay, index * 5 + 2, {
      9: winnerTilt * 0.35 + finalistTilt,
      17: winnerTilt * 0.7 + finalistTilt + dumpedTilt,
      25: winnerTilt * 1.0 + finalistTilt + dumpedTilt * 1.2,
      31: winnerTilt * 1.2 + finalistTilt + dumpedTilt * 1.5,
      32: winnerTilt * 1.4 + finalistTilt + dumpedTilt * 1.8
    })
  };
});

export const datasets = [season8, season7];
