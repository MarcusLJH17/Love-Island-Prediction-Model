"use client";

import { Activity, BarChart3, CalendarPlus, Eye, GitCompare, Save, SlidersHorizontal } from "lucide-react";
import { FormEvent, PointerEvent, useEffect, useMemo, useRef, useState } from "react";
import { datasets } from "../lib/season-data";
import { buildPredictions, defaultSignals, makeProjection, signalLabels } from "../lib/model";
import type { ManualEpisodeEntry, ManualTikTokEntry, SignalKey } from "../lib/types";

type ExportedContestantPrediction = {
  id: string;
  displayName: string;
  probability: number;
  score: number;
  sourceBreakdown: Partial<Record<SignalKey | "social3d" | "social7d", number | null>>;
  sourceAvailable: Partial<Record<SignalKey, boolean>>;
};

type ExportedPredictionPayload = {
  season: number;
  generatedAt: string;
  days: {
    date: string;
    day: number;
    contestants: ExportedContestantPrediction[];
  }[];
};

type SourceHealthPayload = {
  generatedAt: string;
  sources: {
    source: string;
    latestCollectedAt: string | null;
    latestFeatureDate: string | null;
    rawPosts: number;
    mentions: number;
  }[];
};

const chartWidth = 980;
const chartHeight = 420;
const leftPad = 44;
const rightPad = 24;
const topPad = 28;
const bottomPad = 38;
const projectionDays = 12;
const liveDataset = datasets.find((item) => item.season === 8) ?? datasets[0];
const backtestDataset = datasets.find((item) => item.season === 7) ?? datasets[1];

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function todayId() {
  return new Date().toISOString().slice(0, 10);
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

function coord(value: number) {
  return Number(value.toFixed(3));
}

function dayLabel(day: number) {
  return Number.isInteger(day) ? `Day ${day}` : `Day ${day.toFixed(1)}`;
}

function isActiveAt(contestant: { enteredDay: number; exitDay?: number }, day: number) {
  return contestant.enteredDay <= day && (contestant.exitDay == null || contestant.exitDay >= day);
}

export default function Home() {
  const [activeSeason, setActiveSeason] = useState<7 | 8>(8);
  const [signals, setSignals] = useState(defaultSignals);
  const [cursorDay, setCursorDay] = useState(liveDataset.currentDay);
  const [tiktokEntries, setTikTokEntries] = useState<ManualTikTokEntry[]>([]);
  const [episodeEntries, setEpisodeEntries] = useState<ManualEpisodeEntry[]>([]);
  const [exportedPredictions, setExportedPredictions] = useState<ExportedPredictionPayload | null>(null);
  const [sourceHealth, setSourceHealth] = useState<SourceHealthPayload | null>(null);
  const chartRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("season") === "7") {
      setActiveSeason(7);
      setCursorDay(32);
    }
  }, []);

  useEffect(() => {
    refreshExports();
  }, []);

  function refreshExports() {
    fetch("/data/processed/predictions/season8_daily.json", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload: ExportedPredictionPayload | null) => setExportedPredictions(payload))
      .catch(() => setExportedPredictions(null));
    fetch("/data/processed/source_health.json", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload: SourceHealthPayload | null) => setSourceHealth(payload))
      .catch(() => setSourceHealth(null));
  }

  function healthSummary() {
    if (!sourceHealth?.sources.length) return "No source data";
    return sourceHealth.sources.map((source) => `${source.source} ${source.mentions ?? 0}`).join(" / ");
  }

  const dataset = datasets.find((item) => item.season === activeSeason) ?? datasets[0];
  const predictions = useMemo(
    () => buildPredictions(dataset, signals, activeSeason === 8 ? tiktokEntries : [], activeSeason === 8 ? episodeEntries : []),
    [dataset, signals, activeSeason, tiktokEntries, episodeEntries]
  );
  const maxDay = activeSeason === 8 ? dataset.currentDay + projectionDays : dataset.currentDay;
  const selectedDay = clamp(cursorDay, 1, maxDay);
  const activeDay = Math.max(1, Math.floor(Math.min(selectedDay, dataset.currentDay)));
  const xScale = (day: number) => leftPad + ((day - 1) / (maxDay - 1)) * (chartWidth - leftPad - rightPad);
  const yScale = (value: number) => topPad + (1 - value / 0.5) * (chartHeight - topPad - bottomPad);
  const cursorX = xScale(selectedDay);
  const cursorIndex = clamp(Math.round(Math.min(selectedDay, dataset.currentDay)) - 1, 0, dataset.currentDay - 1);
  const projectionMode = activeSeason === 8 && selectedDay > dataset.currentDay;
  const fanMode = selectedDay < maxDay;
  const exportedDay = useMemo(() => {
    if (activeSeason !== 8 || exportedPredictions?.season !== 8) return null;
    const roundedDay = Math.round(activeDay);
    const matches = exportedPredictions.days.filter((item) => item.day === roundedDay);
    return matches[matches.length - 1] ?? null;
  }, [activeDay, activeSeason, exportedPredictions]);
  const exportedById = useMemo(() => {
    return new Map((exportedDay?.contestants ?? []).map((item) => [item.id, item]));
  }, [exportedDay]);

  const ranked = predictions
    .map((prediction) => {
      const historical = prediction.points[cursorIndex]?.probability ?? 0;
      const projection = makeProjection(prediction, cursorIndex, projectionDays, { cursorDay: activeDay, season: activeSeason });
      const projectedValue = projectionMode ? projection[Math.round(selectedDay - dataset.currentDay) - 1] ?? projection[0] : historical;
      const exportedValue = !projectionMode ? exportedById.get(prediction.contestant.id)?.probability : undefined;
      return { ...prediction, displayProbability: exportedValue ?? projectedValue, projection };
    })
    .sort((a, b) => b.displayProbability - a.displayProbability);
  const activeRanked = ranked.filter((item) => isActiveAt(item.contestant, activeDay));
  const topWoman = activeRanked.find((item) => item.contestant.gender === "woman");
  const topMan = activeRanked.find((item) => item.contestant.gender === "man");

  function handlePointer(event: PointerEvent<SVGSVGElement>) {
    const rect = chartRef.current?.getBoundingClientRect();
    if (!rect) return;
    const localX = ((event.clientX - rect.left) / rect.width) * chartWidth;
    const ratio = clamp((localX - leftPad) / (chartWidth - leftPad - rightPad), 0, 1);
    setCursorDay(Math.round(1 + ratio * (maxDay - 1)));
  }

  function handleScrub(value: string) {
    setCursorDay(Number(value));
  }

  function toggleSignal(key: SignalKey) {
    setSignals((current) => ({ ...current, [key]: !current[key] }));
  }

  function selectSeason(season: 7 | 8) {
    setActiveSeason(season);
    setCursorDay(season === 8 ? liveDataset.currentDay : backtestDataset.currentDay);
    window.history.replaceState(null, "", season === 8 ? "/" : "/?season=7");
  }

  async function submitTikTok(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const entry: ManualTikTokEntry = {
      id: crypto.randomUUID(),
      date: todayId(),
      day: dataset.currentDay,
      contestantId: String(form.get("contestantId")),
      positiveSentiment: form.get("positiveSentiment") === "yes",
      visibleEditVolume: Number(form.get("visibleEditVolume")),
      commentTone: Number(form.get("commentTone")),
      viralMomentum: Number(form.get("viralMomentum")),
      notes: String(form.get("notes") ?? "")
    };
    setTikTokEntries((items) => [entry, ...items]);
    await fetch("/api/manual/tiktok", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(entry) });
    refreshExports();
    event.currentTarget.reset();
  }

  async function submitEpisode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const entry: ManualEpisodeEntry = {
      id: crypto.randomUUID(),
      date: todayId(),
      day: dataset.currentDay,
      contestantId: String(form.get("contestantId")),
      episodeEnjoyment: Number(form.get("episodeEnjoyment")),
      gotGoodEdit: form.get("gotGoodEdit") === "yes",
      relationshipStrength: Number(form.get("relationshipStrength")),
      riskOfDumping: Number(form.get("riskOfDumping")),
      notes: String(form.get("notes") ?? "")
    };
    setEpisodeEntries((items) => [entry, ...items]);
    await fetch("/api/manual/episode", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(entry) });
    refreshExports();
    event.currentTarget.reset();
  }

  return (
    <main>
      <section className="topbar">
        <div>
          <h1>IslandEdge - Forecast Workbench</h1>
          <p className="subtitle">{activeSeason === 8 ? `Day ${dataset.currentDay} live forecast` : `${dayLabel(selectedDay)} of ${dataset.currentDay} backtest`}</p>
        </div>
        <div className="score-pill">
          <span>Model mode</span>
          <strong>{activeSeason === 8 ? "Live" : "Backtest"}</strong>
        </div>
        <div className="tabs" aria-label="Season tabs">
          <button type="button" data-season-tab="8" className={activeSeason === 8 ? "active" : ""} onClick={() => selectSeason(8)} onPointerDown={() => selectSeason(8)}>
            <Activity size={16} /> Season 8 Live
          </button>
          <button type="button" data-season-tab="7" className={activeSeason === 7 ? "active" : ""} onClick={() => selectSeason(7)} onPointerDown={() => selectSeason(7)}>
            <GitCompare size={16} /> Season 7 Backtest
          </button>
        </div>
      </section>

      <section className="roster-strip" aria-label={`${dataset.label} islanders`}>
        {activeRanked.map((prediction) => (
          <button className="roster-pill" key={prediction.contestant.id} title={prediction.contestant.name}>
            <IslanderPhoto contestant={prediction.contestant} />
            <span className="dot" style={{ background: prediction.contestant.color }} />
            <strong>{prediction.contestant.displayName}</strong>
            <span>{pct(prediction.displayProbability)}</span>
          </button>
        ))}
      </section>

      <section className="control-band">
        <div className="panel signals">
          <div className="panel-title split-title">
            <span><SlidersHorizontal size={17} /> Source Toggles</span>
            <span className="health-inline"><Activity size={15} /> {healthSummary()}</span>
          </div>
          {(Object.keys(signalLabels) as SignalKey[]).map((key) => (
            <button key={key} className={signals[key] ? "signal on" : "signal"} onClick={() => toggleSignal(key)}>
              <span>{signalLabels[key]}</span>
              <span>{signals[key] ? "On" : "Off"}</span>
            </button>
          ))}
        </div>
        <div className="panel status">
          <div className="panel-title"><BarChart3 size={17} /> Cursor State</div>
          <strong>{projectionMode ? `+${(selectedDay - dataset.currentDay).toFixed(1)}d` : dayLabel(selectedDay)}</strong>
          <span>{projectionMode ? "Momentum projection is shown in the cards." : activeSeason === 7 ? "Backtest simulation starts at the selected historical day." : exportedDay ? "Exported social-signal predictions are shown in the cards." : "Seeded model distribution is shown in the cards."}</span>
        </div>
        <div className="panel status">
          <div className="panel-title"><Activity size={17} /> Source Health</div>
          <strong>{sourceHealth ? new Date(sourceHealth.generatedAt).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) : "Pending"}</strong>
          <span>{sourceHealth?.sources.map((source) => `${source.source}: ${source.mentions ?? 0}`).join(" · ") ?? "No exported source health yet."}</span>
        </div>
      </section>

      <section className="chart-shell panel">
        <div className="chart-heading">
          <div>
            <p>Panel 1</p>
            <h2>{activeSeason === 8 ? `Live forecast - ${dayLabel(selectedDay).toLowerCase()}` : `Backtest - day 1 to ${selectedDay.toFixed(1)}`}</h2>
          </div>
          <span>{activeSeason === 8 ? "Solid = history - dashed = projection" : "Solid = historical model value - dashed = projection"}</span>
        </div>
        <svg
          ref={chartRef}
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          role="img"
          aria-label="Win probability timeline"
          onPointerDown={(event) => {
            event.currentTarget.setPointerCapture(event.pointerId);
            handlePointer(event);
          }}
          onPointerMove={(event) => event.buttons === 1 && handlePointer(event)}
        >
          <rect x={leftPad} y={topPad} width={xScale(dataset.currentDay) - leftPad} height={chartHeight - topPad - bottomPad} className="history-zone" />
          {activeSeason === 8 && <rect x={xScale(dataset.currentDay)} y={topPad} width={xScale(maxDay) - xScale(dataset.currentDay)} height={chartHeight - topPad - bottomPad} className="projection-zone" />}
          {[0.1, 0.2, 0.3, 0.4].map((value) => (
            <g key={value}>
              <line x1={leftPad} x2={chartWidth - rightPad} y1={yScale(value)} y2={yScale(value)} className="grid" />
              <text x={8} y={yScale(value) + 4} className="axis">{pct(value)}</text>
            </g>
          ))}
          {activeRanked.map((prediction, index) => {
            const visibleHistory = prediction.points.filter((point) => point.day >= prediction.contestant.enteredDay && point.day <= Math.min(dataset.currentDay, maxDay));
            const historyPath = visibleHistory.map((point) => `${coord(xScale(point.day))},${coord(yScale(point.probability))}`).join(" ");
            const base = prediction.points[cursorIndex]?.probability ?? 0;
            const fanLength = Math.max(0, Math.ceil(maxDay - selectedDay));
            const projection = makeProjection(prediction, cursorIndex, fanLength, { cursorDay: activeDay, season: activeSeason });
            const projectionPath = projection.map((value, pIndex) => {
              const fanDay = selectedDay + ((pIndex + 1) / Math.max(1, fanLength)) * (maxDay - selectedDay);
              return `${coord(xScale(fanDay))},${coord(yScale(value))}`;
            }).join(" ");
            return (
              <g key={prediction.contestant.id}>
                <polyline points={historyPath} fill="none" stroke={prediction.contestant.color} strokeWidth="2.6" strokeLinecap="round" />
                {fanMode && projectionPath && <polyline points={`${coord(cursorX)},${coord(yScale(base))} ${projectionPath}`} fill="none" stroke={prediction.contestant.color} strokeWidth="1.4" strokeOpacity="0.22" strokeDasharray="4 5" />}
              </g>
            );
          })}
          {activeSeason === 8 && <line x1={xScale(dataset.currentDay)} x2={xScale(dataset.currentDay)} y1={topPad} y2={chartHeight - bottomPad} className="today-line" />}
          <line x1={cursorX} x2={cursorX} y1={topPad - 10} y2={chartHeight - bottomPad + 10} className="cursor-line" />
          <text x={clamp(cursorX - 42, leftPad, chartWidth - 150)} y={topPad - 14} className="cursor-label">
            {projectionMode ? `+${(selectedDay - dataset.currentDay).toFixed(1)}d` : dayLabel(selectedDay)}
          </text>
          <text x={leftPad} y={chartHeight - 10} className="axis">Day 1</text>
          {activeSeason === 8 ? (
            <>
              <text x={xScale(dataset.currentDay) - 32} y={chartHeight - 10} className="axis">Today</text>
              <text x={chartWidth - 116} y={chartHeight - 10} className="axis">Projection</text>
            </>
          ) : (
            <text x={chartWidth - 112} y={chartHeight - 10} className="axis">Finale</text>
          )}
        </svg>
        <div className="scrubber">
          <input
            aria-label="Timeline cursor"
            type="range"
            min="1"
            max={maxDay}
            step="0.1"
            value={selectedDay}
            onInput={(event) => handleScrub(event.currentTarget.value)}
            onChange={(event) => handleScrub(event.currentTarget.value)}
          />
          <div>
            <span>Day 1</span>
            <strong>{projectionMode ? `+${(selectedDay - dataset.currentDay).toFixed(1)}d` : dayLabel(selectedDay)}</strong>
            <span>{activeSeason === 8 ? `Day ${maxDay}` : "Finale"}</span>
          </div>
        </div>
      </section>

      <section className="cards">
        {activeRanked.map((prediction) => {
          const fanDays = Math.max(1, maxDay - selectedDay);
          const low = Math.max(0, Math.min(...prediction.projection, prediction.displayProbability));
          const high = Math.min(0.7, Math.max(...prediction.projection, prediction.displayProbability));
          return (
            <article className="contestant-card" key={prediction.contestant.id}>
              <IslanderPhoto contestant={prediction.contestant} />
              <div>
                <h2>{prediction.contestant.displayName}</h2>
                <p>{prediction.contestant.isOG ? "Original islander" : `Entered day ${prediction.contestant.enteredDay}`}</p>
              </div>
              <strong>{pct(prediction.displayProbability)}</strong>
              {fanMode && <span>{pct(low)} to {pct(high)}</span>}
            </article>
          );
        })}
      </section>

      {activeSeason === 8 ? (
        <section className="forms-grid">
          <form className="panel entry-form" onSubmit={submitTikTok}>
            <div className="panel-title"><Eye size={17} /> TikTok Observation</div>
            <SelectContestant contestants={dataset.contestants.filter((contestant) => isActiveAt(contestant, activeDay))} />
            <YesNo name="positiveSentiment" label="Overall sentiment positive?" />
            <Range name="visibleEditVolume" label="Edit volume seen" />
            <Range name="commentTone" label="Comment tone" />
            <Range name="viralMomentum" label="Viral momentum" />
            <textarea name="notes" placeholder="Short notes" />
            <button className="primary"><Save size={16} /> Save TikTok entry</button>
          </form>

          <form className="panel entry-form" onSubmit={submitEpisode}>
            <div className="panel-title"><CalendarPlus size={17} /> Episode Thoughts</div>
            <SelectContestant contestants={dataset.contestants.filter((contestant) => isActiveAt(contestant, activeDay))} />
            <Range name="episodeEnjoyment" label="How strong was their episode?" />
            <YesNo name="gotGoodEdit" label="Did they get a good edit?" />
            <Range name="relationshipStrength" label="Relationship strength" />
            <Range name="riskOfDumping" label="Risk of dumping" />
            <textarea name="notes" placeholder="Short notes" />
            <button className="primary"><Save size={16} /> Save episode entry</button>
          </form>
        </section>
      ) : (
        <section className="backtest panel">
          <div className="panel-title"><GitCompare size={17} /> Backtest Summary</div>
          <p>The Season 7 seeded backtest ranks the known winners and finalists against the same interpretable feature model used by the live tab.</p>
          <div className="result-row">
            <span>Known winners</span>
            <strong>Amaya / Bryan</strong>
          </div>
          <div className="result-row">
            <span>Top forecast at cursor</span>
            <strong>{[topWoman?.contestant.displayName, topMan?.contestant.displayName].filter(Boolean).join(" / ")}</strong>
          </div>
        </section>
      )}
    </main>
  );
}

function IslanderPhoto({ contestant }: { contestant: { displayName: string; photoUrl: string } }) {
  const [failed, setFailed] = useState(false);

  return (
    <span className="photo">
      <span aria-hidden="true">{contestant.displayName.slice(0, 1)}</span>
      {!failed && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={contestant.photoUrl}
          alt=""
          onError={() => setFailed(true)}
        />
      )}
    </span>
  );
}

function SelectContestant({ contestants }: { contestants: { id: string; name: string; displayName: string }[] }) {
  return (
    <label>
      Contestant
      <select name="contestantId" required defaultValue={contestants[0]?.id}>
        {contestants.map((contestant) => <option value={contestant.id} key={contestant.id}>{contestant.displayName}</option>)}
      </select>
    </label>
  );
}

function YesNo({ name, label }: { name: string; label: string }) {
  return (
    <label>
      {label}
      <select name={name} defaultValue="yes">
        <option value="yes">Yes</option>
        <option value="no">No</option>
      </select>
    </label>
  );
}

function Range({ name, label }: { name: string; label: string }) {
  return (
    <label>
      {label}
      <input name={name} type="range" min="1" max="5" defaultValue="3" />
    </label>
  );
}
