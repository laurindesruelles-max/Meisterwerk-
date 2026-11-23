// MEISTERWERK-Look: dunkle Studio-Werkhalle, Stahl (gebürstet), Glut-Orange; Schrift Inter Black;
// Text wird per Laser ins Metall graviert (kein Tippen – das gehört Goldsmith); Typenschild-Platten statt Papier.
import React from "react";
import {AbsoluteFill, useCurrentFrame, interpolate} from "remotion";
import {s, clamp, ease} from "./lib";

const ORANGE = "#FF6A13", STEEL = "#C9CDD2", GRAPHITE = "#0E0F11", WHITE = "#F3F4F6";
const brushed = "repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0 1px, rgba(0,0,0,0.04) 1px 3px), linear-gradient(180deg,#d9dce0 0%,#aeb3b9 55%,#8d9299 100%)";
const plateCss: React.CSSProperties = {background: brushed, borderRadius: 10, boxShadow: "inset 0 2px 0 rgba(255,255,255,0.7), inset 0 -3px 0 rgba(0,0,0,0.25), 0 18px 40px rgba(0,0,0,0.6)", border: "2px solid #7c8188"};

const Bg: React.FC<{children?: React.ReactNode; hot?: boolean}> = ({children, hot}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: GRAPHITE}}>
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% -10%, rgba(230,235,240,0.30) 0%, rgba(120,125,130,0.10) 35%, transparent 70%)`}} />
      {hot && <AbsoluteFill style={{background: "radial-gradient(ellipse at 50% 55%, rgba(255,106,19,0.28) 0%, transparent 60%)"}} />}
      <AbsoluteFill style={{backgroundImage: "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
        backgroundSize: "80px 80px", backgroundPosition: `${f * 0.25}px 0px`, maskImage: "linear-gradient(180deg, transparent 0%, black 55%, black 100%)",
        transform: "perspective(900px) rotateX(55deg) translateY(260px) scale(1.6)", transformOrigin: "50% 100%"}} />
      {children}
      <AbsoluteFill style={{background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.75) 100%)"}} />
      <div style={{position: "absolute", right: 46, top: 30, fontFamily: "Inter", fontWeight: 900, fontSize: 18, letterSpacing: 2, color: WHITE, opacity: 0.85}}>
        MEISTERWERK<div style={{height: 3, width: 40, background: ORANGE, marginLeft: "auto", marginTop: 2}} /></div>
    </AbsoluteFill>
  );
};

/** Laser-Gravur: Buchstaben erscheinen glühend orange hinter einem Laserpunkt und kühlen ab */
const Write: React.FC<{text: string; at: number; style?: React.CSSProperties}> = ({text, at, style}) => {
  const f = useCurrentFrame(); if (f < s(at)) return null;
  const cps = 22; const n = ((f - s(at)) / 30) * cps;
  return <span style={{fontFamily: "Inter", fontWeight: 800, ...style}}>
    {text.split("").map((c, i) => {
      const age = n - i; if (age < 0) return <span key={i} style={{opacity: 0}}>{c}</span>;
      const heat = Math.max(0, 1 - age / 6);
      return <span key={i} style={{color: heat > 0.05 ? `rgb(255,${Math.round(106 + 120 * (1 - heat))},${Math.round(19 + 200 * (1 - heat))})` : undefined,
        textShadow: heat > 0.05 ? `0 0 ${12 * heat}px ${ORANGE}` : undefined}}>{c}</span>;
    })}
    {n < text.length && <span style={{display: "inline-block", width: 10, height: 10, borderRadius: 5, background: "#fff", boxShadow: `0 0 18px 6px ${ORANGE}`, marginLeft: 2, verticalAlign: "middle"}} />}
  </span>;
};

const Label: React.FC<{text?: string}> = ({text}) => {
  const f = useCurrentFrame(); if (!text) return null;
  const p = interpolate(f, [s(0.05), s(0.5)], [0, 1], {...clamp, easing: ease});
  return <div style={{position: "absolute", left: 80, top: 60, opacity: p, transform: `translateY(${(1 - p) * -20}px)`, ...plateCss, padding: "8px 22px", display: "flex", gap: 12, alignItems: "center"}}>
    <div style={{width: 10, height: 10, borderRadius: 5, background: "#6b7078", boxShadow: "inset 0 1px 1px #000"}} />
    <Write text={text} at={0.15} style={{fontSize: 26, color: "#2b2e33", letterSpacing: 3}} />
  </div>;
};

/** Leuchtende Orange-Linie (wie ein Laserstrahl), gerade oder leicht gebogen */
const Thread: React.FC<{x1: number; y1: number; x2: number; y2: number; p: number; straight?: boolean}> = ({x1, y1, x2, y2, p, straight}) => {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - (straight ? 0 : Math.hypot(x2 - x1, y2 - y1) * 0.15);
  const len = Math.hypot(x2 - x1, y2 - y1) * 1.2; const d = `M${x1},${y1} Q${mx},${my} ${x2},${y2}`;
  return <g><path d={d} fill="none" stroke={ORANGE} strokeOpacity={0.35} strokeWidth={10} strokeDasharray={len} strokeDashoffset={len * (1 - p)} style={{filter: "blur(4px)"}} />
    <path d={d} fill="none" stroke="#FFC48F" strokeWidth={3} strokeDasharray={len} strokeDashoffset={len * (1 - p)} /></g>;
};
/** Niete / Messpunkt aus Stahl mit Orange-Kern */
const Pin: React.FC<{x: number; y: number; k: number}> = ({x, y, k}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <circle r={13} fill="#b7bcc2" stroke="#6f747b" strokeWidth={2} /><circle r={6} fill={ORANGE} style={{filter: `drop-shadow(0 0 6px ${ORANGE})`}} />
  </g>
);

export const T = {
  c: {ink: WHITE, muted: "#8b9097", accent: ORANGE, hot: ORANGE, land: "#23262b", border: "#3b4047", dot: "#FFB27A", hl: (o: number) => `rgba(255,106,19,${0.2 + 0.5 * o})`,
      track: "#3a3e45", panelAccent: "#B8460A", nodeInk: "#2b2e33", panelInk: "#2b2e33", cardInk: "#2b2e33", cardHotInk: WHITE, tileInk: "#2b2e33", bubble: "#9a4a12", sheetInk: "#e9edf2", sheetLine: "rgba(233,237,242,0.25)"},
  font: {head: "Inter", body: "Inter", num: "Inter", mono: "DejaVu Sans Mono, monospace"},
  headWeight: 900, headStyle: {letterSpacing: -1} as React.CSSProperties, iconStroke: 6, iconFilter: undefined as string | undefined, mapFilter: undefined as string | undefined,
  glow: true, borderW: 0.8, tileJitter: 0, gridRows: true, num: {sep: ".", decSep: ","},
  Bg, Write, Label, Thread, Pin,
  tag: {...plateCss, padding: "4px 14px"} as React.CSSProperties, tagText: {color: "#2b2e33"} as React.CSSProperties,
  panel: {...plateCss, padding: "10px 36px"} as React.CSSProperties,
  node: {...plateCss} as React.CSSProperties,
  nodeHot: {background: "#2a1306", border: `3px solid ${ORANGE}`, borderRadius: 10, boxShadow: `0 0 50px ${ORANGE}88`} as React.CSSProperties,
  card: {...plateCss} as React.CSSProperties,
  cardTop: "TYPENSCHILD · NR. 0047", cardTopStyle: {fontFamily: "Inter", fontWeight: 800, fontSize: 22, letterSpacing: 3, color: "#3b3f45"} as React.CSSProperties,
  cardHot: {background: "linear-gradient(180deg,#3a1a08,#160904)", border: `4px solid ${ORANGE}`, borderRadius: 10, boxShadow: `0 0 120px ${ORANGE}99`} as React.CSSProperties,
  tile: {...plateCss, borderRadius: 6} as React.CSSProperties,
  tileHot: {background: "#2a1306", border: `3px solid ${ORANGE}`, borderRadius: 6, boxShadow: `0 0 18px ${ORANGE}`} as React.CSSProperties,
  sheet: {background: "#16324f", border: "2px solid #4f7aa6", boxShadow: "0 20px 60px rgba(0,0,0,0.7)", backgroundImage: "linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)", backgroundSize: "24px 24px"} as React.CSSProperties,
  bar: {...plateCss, borderRadius: 4} as React.CSSProperties,
  barHot: {background: `linear-gradient(180deg,#ff9a4d,${ORANGE} 60%,#b94a0a)`, borderRadius: 4, boxShadow: `0 0 30px ${ORANGE}88`} as React.CSSProperties,
};
