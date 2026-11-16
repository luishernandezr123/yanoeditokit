// Plantilla «pasos» de Ya No Edito · estilo: cuadrícula clara, pasos numerados,
// una tarjeta por paso arriba y tu cara abajo en un marco redondeado.
// Lee todo de montaje.json (props). Render: npx remotion render src/index.tsx Reel out.mp4 --props=public/montaje.json --scale=2
import React from 'react';
import {AbsoluteFill, Audio, Composition, OffthreadVideo, Sequence, interpolate, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Palabra = {texto: string; inicio: number; fin: number};
// Una tarjeta por paso. tipo: terminal | chat | archivo | lista
// lineas: textos; resaltes: [{linea: índice, inicio: s}] pinta esa línea de azul desde ese segundo del reel
type TarjetaDef = {tipo: 'terminal' | 'chat' | 'archivo' | 'lista'; titulo: string; lineas: string[]; final?: string; resaltes?: {linea: number; inicio: number}[]};
type Paso = {n: number; nombre: string; inicio: number; tarjeta: TarjetaDef};
type Montaje = {duracion: number; titulo: {texto: string; etiqueta?: string; inicio: number; fin: number}; pasos: Paso[]; palabras: Palabra[]};

const C = {fondo: '#F4F4F1', linea: '#E2E2DC', tinta: '#111111', azul: '#2563EB', azulSuave: '#DBE6FF', gris: '#6B6B6B', blanco: '#FFFFFF'};
const SANS = '"SF Pro Display", "Helvetica Neue", Arial, sans-serif';
const MONO = '"SF Mono", Menlo, monospace';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Ventana: React.FC<{titulo: string; children: React.ReactNode; style?: React.CSSProperties}> = ({titulo, children, style}) => (
  <div style={{background: C.blanco, borderRadius: 28, boxShadow: '0 18px 50px rgba(0,0,0,0.10)', border: '2px solid #E4E4E0', overflow: 'hidden', ...style}}>
    <div style={{height: 64, display: 'flex', alignItems: 'center', gap: 12, padding: '0 26px', borderBottom: '2px solid #EEEEEA'}}>
      {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <i key={c} style={{width: 16, height: 16, borderRadius: 99, background: c}} />)}
      <span style={{marginLeft: 14, fontFamily: SANS, fontWeight: 700, fontSize: 28, color: C.tinta}}>{titulo}</span>
    </div>
    <div style={{padding: '30px 34px'}}>{children}</div>
  </div>
);

const Tarjeta: React.FC<{paso: Paso; f: number; fps: number; m: Montaje}> = ({paso, f, fps, m}) => {
  const t = f / fps; // segundos desde que empezó el paso
  const ap = (s: number) => interpolate(t, [s, s + 0.35], [0, 1], clamp);
  const d = paso.tarjeta;
  const encendida = (i: number) => (d.resaltes || []).some((r) => r.linea === i && t + paso.inicio >= r.inicio);
  if (d.tipo === 'terminal') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((l, i) => {
        const txt = i === 0 ? l.slice(0, Math.floor(interpolate(t, [0.3, 1.3], [0, l.length], clamp))) : l;
        return <div key={i} style={{opacity: i === 0 ? 1 : ap(1.4 + i * 0.6), fontFamily: MONO, fontSize: 36, color: i === 0 ? C.tinta : C.azul, marginBottom: 14}}>{i === 0 ? '> ' : '✓ '}{txt}{i === 0 && t < 1.5 ? '▌' : ''}</div>;
      })}
      {d.final && <div style={{marginTop: 18, opacity: ap(1.6 + d.lineas.length * 0.6), fontFamily: SANS, fontWeight: 800, fontSize: 44, color: C.tinta}}>{d.final}</div>}
    </Ventana>
  );
  if (d.tipo === 'chat') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((x, i) => (
        <div key={i} style={{opacity: ap(0.5 + i * 1.4), transform: `translateY(${30 * (1 - ap(0.5 + i * 1.4))}px)`, marginBottom: 20, padding: '20px 24px', borderRadius: 18, background: encendida(i) ? C.azulSuave : '#F1F1EE', fontFamily: SANS, fontSize: 34, color: C.tinta}}>{x}</div>
      ))}
      {d.final && <div style={{opacity: ap(0.8 + d.lineas.length * 1.4), fontFamily: SANS, fontWeight: 800, fontSize: 40, color: '#D14343'}}>{d.final}</div>}
    </Ventana>
  );
  if (d.tipo === 'archivo') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((txt, i) => {
        const h = txt.startsWith('#'); const on = encendida(i);
        return <div key={i} style={{opacity: ap(0.3 + i * 0.25), fontFamily: MONO, fontSize: h ? 36 : 32, fontWeight: h ? 800 : 500, color: on ? C.azul : C.tinta, background: on ? C.azulSuave : 'transparent', borderRadius: 10, padding: '6px 12px', marginBottom: 8}}>{txt}</div>;
      })}
    </Ventana>
  );
  const pasos = d.lineas;
  return (
    <Ventana titulo={d.titulo}>
      {pasos.map((x, i) => (
        <div key={x} style={{display: 'flex', alignItems: 'center', gap: 22, marginBottom: 26, opacity: ap(0.4 + i * 1.2), transform: `translateX(${40 * (1 - ap(0.4 + i * 1.2))}px)`}}>
          <div style={{width: 64, height: 64, borderRadius: 16, background: C.azul, color: C.blanco, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 34}}>{i + 1}</div>
          <div style={{fontFamily: SANS, fontWeight: 700, fontSize: 40, color: C.tinta}}>{x}</div>
        </div>
      ))}
    </Ventana>
  );
};

const Subtitulo: React.FC<{m: Montaje; t: number; arriba: number}> = ({m, t, arriba}) => {
  // grupos de hasta 4 palabras; se muestra el grupo que contiene el instante actual
  const grupos: Palabra[][] = [];
  m.palabras.forEach((w) => {const g = grupos[grupos.length - 1]; if (!g || g.length >= 4 || /[.,?]$/.test(g[g.length - 1].texto)) grupos.push([w]); else g.push(w);});
  const g = grupos.find((x) => t >= x[0].inicio - 0.05 && t <= x[x.length - 1].fin + 0.25);
  if (!g) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: arriba, display: 'flex', justifyContent: 'center'}}>
      <div style={{background: C.blanco, borderRadius: 999, padding: '16px 34px', boxShadow: '0 10px 30px rgba(0,0,0,0.18)', fontFamily: SANS, fontWeight: 700, fontSize: 46, color: C.tinta, display: 'flex', gap: 14}}>
        {g.map((w, i) => <span key={i} style={{color: t >= w.inicio && t <= w.fin + 0.05 ? C.azul : C.tinta}}>{w.texto}</span>)}
      </div>
    </div>
  );
};

const Reel: React.FC<Montaje> = (m) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const enGancho = t < m.titulo.fin;
  const pasoActual = [...m.pasos].reverse().find((p) => t >= p.inicio);
  const entradaCuerpo = spring({frame: f - Math.round(m.titulo.fin * fps), fps, config: {damping: 200}});
  return (
    <AbsoluteFill style={{background: C.fondo, backgroundImage: `linear-gradient(${C.linea} 2px, transparent 2px), linear-gradient(90deg, ${C.linea} 2px, transparent 2px)`, backgroundSize: '48px 48px'}}>
      <Audio src={staticFile('musica.wav')} volume={1} />
      {m.pasos.map((p) => <Sequence key={p.n} from={Math.round(p.inicio * fps) - 4} durationInFrames={30}><Audio src={staticFile('whoosh.wav')} volume={0.9} /></Sequence>)}
      {m.pasos.flatMap((p) => (p.tarjeta.resaltes || []).map((r) => <Sequence key={`${p.n}-${r.linea}`} from={Math.round(r.inicio * fps)} durationInFrames={10}><Audio src={staticFile('pop.wav')} volume={0.6} /></Sequence>))}

      {/* Cara: pantalla completa en el gancho; después, marco redondeado abajo */}
      {(() => {
        const k = enGancho ? 0 : entradaCuerpo;
        const top = interpolate(k, [0, 1], [0, 1010]);
        const left = interpolate(k, [0, 1], [0, 90]);
        const w = interpolate(k, [0, 1], [1080, 900]);
        const h = interpolate(k, [0, 1], [1920, 700]);
        return (
          <div style={{position: 'absolute', left, top, width: w, height: h, borderRadius: 40 * k, overflow: 'hidden', boxShadow: k > 0 ? '0 20px 60px rgba(0,0,0,0.18)' : 'none'}}>
            <OffthreadVideo src={staticFile('base.mp4')} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 32%'}} />
          </div>
        );
      })()}

      {enGancho && (
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 45%)'}}>
          <div style={{position: 'absolute', top: 210, left: 80, right: 80, textAlign: 'center', opacity: interpolate(t, [0.1, 0.5], [0, 1], clamp), transform: `translateY(${interpolate(t, [0.1, 0.6], [40, 0], clamp)}px)`}}>
            {m.titulo.etiqueta && <div style={{display: 'inline-block', fontFamily: MONO, fontWeight: 800, fontSize: 34, color: C.blanco, background: C.azul, borderRadius: 14, padding: '10px 22px', marginBottom: 26}}>{m.titulo.etiqueta}</div>}
            <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 92, lineHeight: 1.04, color: C.blanco, textShadow: '0 4px 24px rgba(0,0,0,0.4)'}}>{m.titulo.texto}</div>
          </div>
        </AbsoluteFill>
      )}

      {!enGancho && pasoActual && (
        <>
          <div style={{position: 'absolute', top: 120, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 18, opacity: entradaCuerpo}}>
            {m.pasos.map((p) => {const on = p.n === pasoActual.n; return <div key={p.n} style={{width: 92, height: 92, borderRadius: 22, background: on ? C.azul : C.blanco, color: on ? C.blanco : '#9A9A9A', border: on ? 'none' : '2px solid #DCDCD6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 44, transform: `scale(${on ? 1.08 : 1})`, boxShadow: on ? '0 10px 24px rgba(37,99,235,0.35)' : 'none'}}>{p.n}</div>;})}
          </div>
          <div style={{position: 'absolute', top: 236, left: 0, right: 0, textAlign: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 40, color: C.tinta, opacity: entradaCuerpo}}>{pasoActual.nombre}</div>
          {m.pasos.map((p, i) => {
            const fin = m.pasos[i + 1] ? m.pasos[i + 1].inicio : m.duracion;
            const desde = Math.round(p.inicio * fps);
            return (
              <Sequence key={p.n} from={desde} durationInFrames={Math.max(1, Math.round((fin - p.inicio) * fps))}>
                <SlideIn><Tarjeta paso={p} f={0} fps={fps} m={m} /></SlideIn>
              </Sequence>
            );
          })}
        </>
      )}

      <Subtitulo m={m} t={t} arriba={enGancho ? 1520 : 1745} />
    </AbsoluteFill>
  );
};

// Envuelve la tarjeta: entra deslizando desde la derecha y le pasa el frame local
const SlideIn: React.FC<{children: React.ReactElement}> = ({children}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 18, stiffness: 120}});
  return (
    <div style={{position: 'absolute', left: 90, top: 310, width: 900, transform: `translateX(${interpolate(s, [0, 1], [700, 0])}px)`, opacity: s}}>
      {React.cloneElement(children, {f})}
    </div>
  );
};

const Root: React.FC = () => (
  <Composition id="Reel" component={Reel as any} fps={30} width={1080} height={1920}
    defaultProps={{duracion: 5, titulo: {texto: '', inicio: 0, fin: 1}, pasos: [], palabras: []}}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as Montaje).duracion * 30)})} />
);
registerRoot(Root);
