"use client";

import { Activity, BarChart3, CalendarPlus, Eye, GitCompare, Save, SlidersHorizontal } from "lucide-react";
import { FormEvent, PointerEvent, useMemo, useRef, useState } from "react";
import { datasets } from "../lib/season-data";
import { buildPredictions, defaultSignals, makeProjection, signalLabels } from "../lib/model";
import type { ManualEpisodeEntry, ManualTikTokEntry, SignalKey } from "../lib/types";

const chartWidth = 980;
const chartHeight = 420;
const leftPad = 44;
const rightPad = 24;
const topPad = 28;
const bottomPad = 38;
const projectionDays = 12;

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

export default function Home() {
  const [activeSeason, setActiveSeason] = useState<7 | 8>(8);
  const [signals, setSignals] = useState(defaultSignals);
  const [cursorDay, setCursorDay] = useState(28);
  const [tiktokEntries, setTikTokEntries] = useState<ManualTikTokEntry[]>([]);
  const [episodeEntries, setEpisodeEntries] = useState<ManualEpisodeEntry[]>([]);
  const chartRef = useRef<SVGSVGElement | null>(null);

  const dataset = datasets.find((item) => item.season === activeSeason) ?? datasets[0];
  const predictions = useMemo(
    () => buildPredictions(dataset, signals, activeSeason === 8 ? tiktokEntries : [], activeSeason === 8 ? episodeEntries : []),
    [dataset, signals, activeSeason, tiktokEntries, episodeEntries]
  );
  const maxDay = dataset.currentDay + projectionDays;
  const xScale = (day: number) => leftPad + ((day - 1) / (maxDay - 1)) * (chartWidth - leftPad - rightPad);
  const yScale = (value: number) => topPad + (1 - value / 0.34) * (chartHeight - topPad - bottomPad);
  const cursorX = xScale(cursorDay);
  const cursorIndex = clamp(Math.round(cursorDay) - 1, 0, dataset.currentDay - 1);
  const projectionMode = cursorDay > dataset.currentDay;

  const ranked = predictions
    .map((prediction, index) => {
      const historical = prediction.points[cursorIndex]?.probability ?? 0;
      const projection = makeProjection(prediction.points[dataset.currentDay - 1]?.probability ?? historical, projectionDays, index);
      const projectedValue = projectionMode ? projection[Math.round(cursorDay - dataset.currentDay) - 1] ?? projection[0] : historical;
      return { ...prediction, displayProbability: projectedValue, projection };
    })
    .sort((a, b) => b.displayProbability - a.displayProbability);

  function handlePointer(event: PointerEvent<SVGSVGElement>) {
    const rect = chartRef.current?.getBoundingClientRect();
    if (!rect) return;
    const localX = event.clientX - rect.left;
    const ratio = clamp((localX - leftPad) / (chartWidth - leftPad - rightPad), 0, 1);
    setCursorDay(Math.round(1 + ratio * (maxDay - 1)));
  }

  function toggleSignal(key: SignalKey) {
    setSignals((current) => ({ ...current, [key]: !current[key] }));
  }

  function submitTikTok(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const entry: ManualTikTokEntry = {
      id: crypto.randomUUID(),
      date: todayId(),
      contestantId: String(form.get("contestantId")),
      positiveSentiment: form.get("positiveSentiment") === "yes",
      visibleEditVolume: Number(form.get("visibleEditVolume")),
      commentTone: Number(form.get("commentTone")),
      viralMomentum: Number(form.get("viralMomentum")),
      notes: String(form.get("notes") ?? "")
    };
    setTikTokEntries((items) => [entry, ...items]);
    event.currentTarget.reset();
  }

  function submitEpisode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const entry: ManualEpisodeEntry = {
      id: crypto.randomUUID(),
      date: todayId(),
      contestantId: String(form.get("contestantId")),
      episodeEnjoyment: Number(form.get("episodeEnjoyment")),
      gotGoodEdit: form.get("gotGoodEdit") === "yes",
      relationshipStrength: Number(form.get("relationshipStrength")),
      riskOfDumping: Number(form.get("riskOfDumping")),
      notes: String(form.get("notes") ?? "")
    };
    setEpisodeEntries((items) => [entry, ...items]);
    event.currentTarget.reset();
  }

  return (
    <main>
      <section className="topbar">
        <div>
          <p className="eyebrow">IslandEdge</p>
          <h1>Love Island USA forecast lab</h1>
        </div>
        <div className="tabs" aria-label="Season tabs">
          <button className={activeSeason === 8 ? "active" : ""} onClick={() => { setActiveSeason(8); setCursorDay(28); }}>
            <Activity size={16} /> Season 8 Live
          </button>
          <button className={activeSeason === 7 ? "active" : ""} onClick={() => { setActiveSeason(7); setCursorDay(32); }}>
            <GitCompare size={16} /> Season 7 Backtest
          </button>
        </div>
      </section>

      <section className="control-band">
        <div className="panel signals">
          <div className="panel-title"><SlidersHorizontal size={17} /> Source Toggles</div>
          {(Object.keys(signalLabels) as SignalKey[]).map((key) => (
            <button key={key} className={signals[key] ? "signal on" : "signal"} onClick={() => toggleSignal(key)}>
              <span>{signalLabels[key]}</span>
              <span>{signals[key] ? "On" : "Off"}</span>
            </button>
          ))}
        </div>
        <div className="panel status">
          <div className="panel-title"><BarChart3 size={17} /> Cursor State</div>
          <strong>{cursorDay <= dataset.currentDay ? `Day ${cursorDay}` : `+${cursorDay - dataset.currentDay}d projection`}</strong>
          <span>{projectionMode ? "Monte Carlo fan values are shown in the cards." : "Historical model distribution is shown in the cards."}</span>
        </div>
      </section>

      <section className="chart-shell">
        <svg
          ref={chartRef}
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          role="img"
          aria-label="Win probability timeline"
          onPointerDown={handlePointer}
          onPointerMove={(event) => event.buttons === 1 && handlePointer(event)}
        >
          <rect x={leftPad} y={topPad} width={xScale(dataset.currentDay) - leftPad} height={chartHeight - topPad - bottomPad} className="history-zone" />
          <rect x={xScale(dataset.currentDay)} y={topPad} width={xScale(maxDay) - xScale(dataset.currentDay)} height={chartHeight - topPad - bottomPad} className="projection-zone" />
          {[0.1, 0.2, 0.3].map((value) => (
            <g key={value}>
              <line x1={leftPad} x2={chartWidth - rightPad} y1={yScale(value)} y2={yScale(value)} className="grid" />
              <text x={8} y={yScale(value) + 4} className="axis">{pct(value)}</text>
            </g>
          ))}
          {predictions.map((prediction, index) => {
            const historyPath = prediction.points.map((point) => `${coord(xScale(point.day))},${coord(yScale(point.probability))}`).join(" ");
            const last = prediction.points[dataset.currentDay - 1]?.probability ?? 0;
            const projection = makeProjection(last, projectionDays, index);
            const projectionPath = projection.map((value, pIndex) => `${coord(xScale(dataset.currentDay + pIndex + 1))},${coord(yScale(value))}`).join(" ");
            return (
              <g key={prediction.contestant.id}>
                <polyline points={historyPath} fill="none" stroke={prediction.contestant.color} strokeWidth="2.6" strokeLinecap="round" />
                <polyline points={`${coord(xScale(dataset.currentDay))},${coord(yScale(last))} ${projectionPath}`} fill="none" stroke={prediction.contestant.color} strokeWidth="1.4" strokeOpacity="0.22" />
              </g>
            );
          })}
          <line x1={xScale(dataset.currentDay)} x2={xScale(dataset.currentDay)} y1={topPad} y2={chartHeight - bottomPad} className="today-line" />
          <line x1={cursorX} x2={cursorX} y1={topPad - 10} y2={chartHeight - bottomPad + 10} className="cursor-line" />
          <text x={clamp(cursorX - 42, leftPad, chartWidth - 150)} y={topPad - 14} className="cursor-label">
            {cursorDay <= dataset.currentDay ? `Day ${cursorDay}` : `+${cursorDay - dataset.currentDay}d projection`}
          </text>
          <text x={leftPad} y={chartHeight - 10} className="axis">Day 1</text>
          <text x={xScale(dataset.currentDay) - 32} y={chartHeight - 10} className="axis">Today</text>
          <text x={chartWidth - 116} y={chartHeight - 10} className="axis">Projection</text>
        </svg>
      </section>

      <section className="cards">
        {ranked.slice(0, 8).map((prediction) => {
          const low = Math.max(0, prediction.displayProbability - Math.sqrt(Math.max(1, cursorDay - dataset.currentDay)) * 0.018);
          const high = Math.min(0.7, prediction.displayProbability + Math.sqrt(Math.max(1, cursorDay - dataset.currentDay)) * 0.018);
          return (
            <article className="contestant-card" key={prediction.contestant.id}>
              <div className="swatch" style={{ background: prediction.contestant.color }} />
              <div>
                <h2>{prediction.contestant.name}</h2>
                <p>{prediction.contestant.isOG ? "Original islander" : `Entered day ${prediction.contestant.enteredDay}`}</p>
              </div>
              <strong>{pct(prediction.displayProbability)}</strong>
              {projectionMode && <span>{pct(low)} to {pct(high)}</span>}
            </article>
          );
        })}
      </section>

      {activeSeason === 8 ? (
        <section className="forms-grid">
          <form className="panel entry-form" onSubmit={submitTikTok}>
            <div className="panel-title"><Eye size={17} /> TikTok Observation</div>
            <SelectContestant contestants={dataset.contestants} />
            <YesNo name="positiveSentiment" label="Overall sentiment positive?" />
            <Range name="visibleEditVolume" label="Edit volume seen" />
            <Range name="commentTone" label="Comment tone" />
            <Range name="viralMomentum" label="Viral momentum" />
            <textarea name="notes" placeholder="Short notes" />
            <button className="primary"><Save size={16} /> Save TikTok entry</button>
          </form>

          <form className="panel entry-form" onSubmit={submitEpisode}>
            <div className="panel-title"><CalendarPlus size={17} /> Episode Thoughts</div>
            <SelectContestant contestants={dataset.contestants} />
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
            <strong>Amaya Espinal / Bryan Arenales</strong>
          </div>
          <div className="result-row">
            <span>Top forecast at finale cursor</span>
            <strong>{ranked.slice(0, 2).map((item) => item.contestant.name).join(" / ")}</strong>
          </div>
        </section>
      )}
    </main>
  );
}

function SelectContestant({ contestants }: { contestants: { id: string; name: string }[] }) {
  return (
    <label>
      Contestant
      <select name="contestantId" required defaultValue={contestants[0]?.id}>
        {contestants.map((contestant) => <option value={contestant.id} key={contestant.id}>{contestant.name}</option>)}
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
