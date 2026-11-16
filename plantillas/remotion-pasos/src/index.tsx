// Plantilla «pasos» de Ya No Edito · estilo: cuadrícula clara, tarjetas, subtítulo en píldora.
// Modo dinámico (montaje con "escenas"): la cara alterna entre pantalla completa (cara) y un marco abajo con una
// tarjeta arriba (tarjeta); la demo puede ir a pantalla completa (pantalla). Zoom en cada corte y golpes de texto.
// Montajes viejos con "pasos" siguen funcionando: se convierten en escenas.
// Lee todo de montaje.json (props). Render: npx remotion render src/index.tsx Reel out.mp4 --props=public/montaje.json --scale=2
import React from 'react';
import {AbsoluteFill, Audio, Composition, OffthreadVideo, Sequence, interpolate, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Palabra = {texto: string; inicio: number; fin: number};
// tipo: terminal | chat | archivo | lista | boton | dato
// lineas: textos; aparece: segundo del reel en que entra cada línea (lo calcula cortar.py desde "tiempos")
type TarjetaDef = {tipo: 'terminal' | 'chat' | 'archivo' | 'lista' | 'boton' | 'dato'; titulo: string; lineas: string[]; final?: string; aparece?: number[]; resaltes?: {linea: number; inicio: number}[]};
type Escena = {inicio: number; modo: 'cara' | 'tarjeta' | 'pantalla'; tarjeta?: TarjetaDef; paso?: {n: number; texto: string}};
type Golpe = {inicio: number; texto: string; color?: 'azul' | 'verde' | 'rojo' | 'amarillo'};
type Paso = {n: number; nombre: string; inicio: number; tarjeta: TarjetaDef};
type Montaje = {duracion: number; titulo: {texto: string; etiqueta?: string; inicio: number; fin: number}; pasos?: Paso[]; escenas?: Escena[]; golpes?: Golpe[]; cortes?: number[]; palabras: Palabra[]};

const C = {fondo: '#F4F4F1', linea: '#E2E2DC', tinta: '#111111', azul: '#2563EB', azulSuave: '#DBE6FF', gris: '#6B6B6B', blanco: '#FFFFFF'};
const GOLPE = {azul: '#2563EB', verde: '#16A34A', rojo: '#E11D48', amarillo: '#F5B400'};
const SANS = '"SF Pro Display", "Helvetica Neue", Arial, sans-serif';
const MONO = '"SF Mono", Menlo, monospace';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Dónde va el video en cada modo (lienzo 1080x1920)
type Caja = {x: number; y: number; w: number; h: number; r: number};
const CAJA: Record<Escena['modo'], Caja> = {
  cara: {x: 0, y: 0, w: 1080, h: 1920, r: 0},
  pantalla: {x: 0, y: 0, w: 1080, h: 1920, r: 0},
  tarjeta: {x: 60, y: 880, w: 960, h: 780, r: 44},
};

const aEscenas = (m: Montaje): Escena[] =>
  m.escenas && m.escenas.length ? m.escenas
    : [{inicio: 0, modo: 'cara'}, ...(m.pasos || []).map((p) => ({inicio: p.inicio, modo: 'tarjeta' as const, tarjeta: p.tarjeta, paso: {n: p.n, texto: p.nombre}}))];

const Ventana: React.FC<{titulo: string; children: React.ReactNode}> = ({titulo, children}) => (
  <div style={{background: C.blanco, borderRadius: 34, boxShadow: '0 24px 60px rgba(0,0,0,0.14)', border: '2px solid #E4E4E0', overflow: 'hidden'}}>
    <div style={{height: 76, display: 'flex', alignItems: 'center', gap: 12, padding: '0 30px', borderBottom: '2px solid #EEEEEA'}}>
      {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <i key={c} style={{width: 18, height: 18, borderRadius: 99, background: c}} />)}
      <span style={{marginLeft: 14, fontFamily: SANS, fontWeight: 700, fontSize: 34, color: C.tinta}}>{titulo}</span>
    </div>
    <div style={{padding: '34px 38px', minHeight: 500}}>{children}</div>
  </div>
);

// t = segundos desde que empezó la escena; t0 = segundo del reel en que empezó
const Tarjeta: React.FC<{d: TarjetaDef; t: number; t0: number}> = ({d, t, t0}) => {
  const ap = (s: number) => interpolate(t, [s, s + 0.3], [0, 1], clamp);
  const cuando = (i: number, porDefecto: number) => (d.aparece && d.aparece[i] !== undefined ? d.aparece[i] - t0 : porDefecto);
  const encendida = (i: number) => (d.resaltes || []).some((r) => r.linea === i && t + t0 >= r.inicio);
  const ultima = d.lineas.length ? cuando(d.lineas.length - 1, 0.4 + (d.lineas.length - 1) * 1.2) : 0;
  if (d.tipo === 'dato') {
    const s = interpolate(t, [0.1, 0.45], [0.4, 1], {...clamp, easing: (x) => 1 - Math.pow(1 - x, 3)});
    return (
      <Ventana titulo={d.titulo}>
        <div style={{display: 'flex', alignItems: 'center', gap: 34}}>
          <div style={{fontFamily: SANS, fontWeight: 900, fontSize: 340, lineHeight: 0.9, color: C.azul, transform: `scale(${s})`, transformOrigin: 'left center'}}>{d.lineas[0]}</div>
          <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 76, lineHeight: 1.05, color: C.tinta, opacity: ap(0.35)}}>{d.lineas[1]}</div>
        </div>
        {d.final && <div style={{marginTop: 22, display: 'inline-block', opacity: ap(0.8), fontFamily: SANS, fontWeight: 800, fontSize: 44, color: C.blanco, background: '#16A34A', borderRadius: 999, padding: '12px 30px'}}>{d.final}</div>}
      </Ventana>
    );
  }
  if (d.tipo === 'boton') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((x, i) => <div key={i} style={{opacity: ap(0.2 + i * 0.4), fontFamily: SANS, fontWeight: i ? 500 : 800, fontSize: i ? 40 : 46, color: i ? C.gris : C.tinta, marginBottom: 16}}>{x}</div>)}
      {d.final && (() => {const k = ap(0.9); const pulso = 1 + 0.05 * Math.sin(Math.max(0, t - 1.2) * 7) * k; return (
        <div style={{marginTop: 18, display: 'inline-block', opacity: k, transform: `scale(${pulso})`, transformOrigin: 'left center', fontFamily: SANS, fontWeight: 800, fontSize: 46, color: C.blanco, background: C.azul, borderRadius: 18, padding: '18px 34px', boxShadow: `0 0 ${40 * k}px rgba(37,99,235,0.55)`}}>{d.final}</div>
      );})()}
    </Ventana>
  );
  if (d.tipo === 'terminal') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((l, i) => {
        const txt = i === 0 ? l.slice(0, Math.floor(interpolate(t, [0.3, 1.3], [0, l.length], clamp))) : l;
        return <div key={i} style={{opacity: i === 0 ? 1 : ap(cuando(i, 1.4 + i * 0.6)), fontFamily: MONO, fontSize: 42, color: i === 0 ? C.tinta : C.azul, marginBottom: 16}}>{i === 0 ? '> ' : '✓ '}{txt}{i === 0 && t < 1.5 ? '▌' : ''}</div>;
      })}
      {d.final && <div style={{marginTop: 18, opacity: ap(ultima + 0.6), fontFamily: SANS, fontWeight: 800, fontSize: 50, color: C.tinta}}>{d.final}</div>}
    </Ventana>
  );
  if (d.tipo === 'chat') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((x, i) => {const k = ap(cuando(i, 0.5 + i * 1.4)); return (
        <div key={i} style={{opacity: k, transform: `translateY(${30 * (1 - k)}px) scale(${0.92 + 0.08 * k})`, transformOrigin: 'left center', marginBottom: 22, padding: '22px 28px', borderRadius: 22, background: encendida(i) ? C.azulSuave : '#F1F1EE', fontFamily: SANS, fontWeight: 700, fontSize: 54, color: C.tinta}}>{x}</div>
      );})}
      {d.final && <div style={{opacity: ap(ultima + 0.9), fontFamily: SANS, fontWeight: 800, fontSize: 48, color: '#E11D48'}}>{d.final}</div>}
    </Ventana>
  );
  if (d.tipo === 'archivo') return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((txt, i) => {
        const h = txt.startsWith('#'); const on = encendida(i);
        return <div key={i} style={{opacity: ap(cuando(i, 0.3 + i * 0.25)), fontFamily: MONO, fontSize: h ? 40 : 36, fontWeight: h ? 800 : 500, color: on ? C.azul : C.tinta, background: on ? C.azulSuave : 'transparent', borderRadius: 10, padding: '6px 12px', marginBottom: 8}}>{txt}</div>;
      })}
    </Ventana>
  );
  return (
    <Ventana titulo={d.titulo}>
      {d.lineas.map((x, i) => {const s0 = cuando(i, 0.4 + i * 1.2); const k = ap(s0); const activa = t >= s0 && (i === d.lineas.length - 1 || t < cuando(i + 1, 0.4 + (i + 1) * 1.2)); return (
        <div key={x} style={{display: 'flex', alignItems: 'center', gap: 28, marginBottom: 40, opacity: k, transform: `translateX(${50 * (1 - k)}px)`}}>
          <div style={{width: 96, height: 96, borderRadius: 24, background: activa ? C.azul : C.tinta, color: C.blanco, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 50, transform: `scale(${activa ? 1.08 : 1})`}}>{i + 1}</div>
          <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 60, lineHeight: 1.1, color: activa ? C.tinta : '#3A3A3A'}}>{x}</div>
        </div>
      );})}
    </Ventana>
  );
};

const Subtitulo: React.FC<{m: Montaje; t: number; arriba: number}> = ({m, t, arriba}) => {
  // grupos de hasta 4 palabras; se muestra el grupo que contiene el instante actual
  const grupos: Palabra[][] = [];
  m.palabras.forEach((w) => {const g = grupos[grupos.length - 1]; if (!g || g.length >= 4 || /[.,?]$/.test(g[g.length - 1].texto)) grupos.push([w]); else g.push(w);});
  const g = grupos.find((x) => t >= x[0].inicio - 0.05 && t <= x[x.length - 1].fin + 0.25);
  if (!g) return null;
  const k = interpolate(t, [g[0].inicio - 0.05, g[0].inicio + 0.08], [0.85, 1], clamp);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: arriba, display: 'flex', justifyContent: 'center'}}>
      <div style={{background: C.blanco, borderRadius: 999, padding: '18px 38px', boxShadow: '0 12px 34px rgba(0,0,0,0.22)', fontFamily: SANS, fontWeight: 800, fontSize: 52, color: C.tinta, display: 'flex', gap: 16, transform: `scale(${k})`}}>
        {g.map((w, i) => {const on = t >= w.inicio && t <= w.fin + 0.05; return <span key={i} style={{color: on ? C.azul : C.tinta}}>{w.texto}</span>;})}
      </div>
    </div>
  );
};

const GolpeTxt: React.FC<{g: Golpe; t: number; arriba: number}> = ({g, t, arriba}) => {
  const {fps} = useVideoConfig();
  const dt = t - g.inicio;
  if (dt < 0 || dt > 1.3) return null;
  const s = spring({frame: dt * fps, fps, config: {damping: 9, stiffness: 180}});
  const salida = interpolate(dt, [1.1, 1.3], [1, 0], clamp);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: arriba, display: 'flex', justifyContent: 'center', opacity: salida}}>
      <div style={{transform: `scale(${s}) rotate(-4deg)`, background: GOLPE[g.color || 'azul'], color: C.blanco, fontFamily: SANS, fontWeight: 900, fontSize: Math.min(110, Math.floor(860 / (0.72 * g.texto.length))), letterSpacing: -2, padding: '18px 44px', borderRadius: 26, boxShadow: '0 20px 50px rgba(0,0,0,0.35)', whiteSpace: 'nowrap'}}>{g.texto}</div>
    </div>
  );
};

const Reel: React.FC<Montaje> = (m) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const escenas = aEscenas(m);
  const golpes = m.golpes || [];
  const iE = Math.max(0, escenas.findIndex((e, i) => t >= e.inicio && (!escenas[i + 1] || t < escenas[i + 1].inicio)));
  const esc = escenas[iE];
  const prev = escenas[iE - 1] || esc;
  const enTitulo = t < m.titulo.fin;

  // Caja del video: viaja con un resorte desde la caja de la escena anterior
  const k = spring({frame: f - Math.round(esc.inicio * fps), fps, config: {damping: 16, stiffness: 150}});
  const A = CAJA[prev.modo], B = CAJA[esc.modo];
  const caja = {x: A.x + (B.x - A.x) * k, y: A.y + (B.y - A.y) * k, w: A.w + (B.w - A.w) * k, h: A.h + (B.h - A.h) * k, r: A.r + (B.r - A.r) * k};

  // Zoom: alterna normal / cerca en cada corte real, empuje lento y un latido en cada golpe
  const cortes = m.cortes && m.cortes.length ? m.cortes : escenas.map((e) => e.inicio);
  const iC = Math.max(0, cortes.filter((c) => t >= c).length - 1);
  const desdeCorte = t - (cortes[iC] || 0);
  const cerca = esc.modo === 'tarjeta' ? 1.04 : 1.14;
  const punch = iC % 2 === 1 ? cerca : 1;
  const empuje = 1 + Math.min(desdeCorte, 6) * 0.006;
  const latido = golpes.reduce((acc, g) => {const d = t - g.inicio; return d >= 0 && d < 0.35 ? acc + 0.05 * (1 - d / 0.35) : acc;}, 0);
  const zoom = punch * empuje + latido;

  const mostrarFondo = esc.modo === 'tarjeta' || prev.modo === 'tarjeta';
  const pasosNum = escenas.filter((e) => e.paso);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {mostrarFondo && <AbsoluteFill style={{background: C.fondo, backgroundImage: `linear-gradient(${C.linea} 2px, transparent 2px), linear-gradient(90deg, ${C.linea} 2px, transparent 2px)`, backgroundSize: '48px 48px'}} />}
      <Audio src={staticFile('musica.wav')} />
      <Audio src={staticFile('efectos.wav')} />

      <div style={{position: 'absolute', left: caja.x, top: caja.y, width: caja.w, height: caja.h, borderRadius: caja.r, overflow: 'hidden', boxShadow: caja.r > 1 ? '0 24px 70px rgba(0,0,0,0.25)' : 'none'}}>
        <OffthreadVideo src={staticFile('base.mp4')} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 34%', transform: `scale(${zoom})`, transformOrigin: '50% 34%'}} />
      </div>

      {/* Tarjeta de la escena, entra deslizando */}
      {escenas.map((e, i) => {
        if (e.modo !== 'tarjeta' || !e.tarjeta) return null;
        const fin = escenas[i + 1] ? escenas[i + 1].inicio : m.duracion;
        return (
          <Sequence key={i} from={Math.round(e.inicio * fps)} durationInFrames={Math.max(1, Math.round((fin - e.inicio) * fps))}>
            <Entrada arriba={e.paso ? 270 : 170}><TarjetaViva d={e.tarjeta} t0={e.inicio} /></Entrada>
          </Sequence>
        );
      })}

      {/* Chip del paso (tarjeta o pantalla) */}
      {esc.paso && !enTitulo && (() => {
        const kk = spring({frame: f - Math.round(esc.inicio * fps), fps, config: {damping: 14, stiffness: 160}});
        return (
          <div style={{position: 'absolute', top: esc.modo === 'pantalla' ? 150 : 150, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14}}>
            <div style={{display: 'flex', alignItems: 'center', gap: 18, background: C.blanco, borderRadius: 999, padding: '12px 34px 12px 12px', boxShadow: '0 14px 40px rgba(0,0,0,0.3)', transform: `translateY(${-60 * (1 - kk)}px) scale(${0.8 + 0.2 * kk})`, opacity: kk}}>
              <div style={{width: 76, height: 76, borderRadius: 999, background: C.azul, color: C.blanco, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontWeight: 900, fontSize: 42}}>{esc.paso.n}</div>
              <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 46, color: C.tinta}}>{esc.paso.texto}</div>
              {pasosNum.length > 1 && <div style={{fontFamily: SANS, fontWeight: 700, fontSize: 32, color: C.gris}}>de {pasosNum[pasosNum.length - 1].paso!.n}</div>}
            </div>
          </div>
        );
      })()}

      {enTitulo && (
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 48%)'}}>
          <div style={{position: 'absolute', top: 200, left: 70, right: 70, textAlign: 'center'}}>
            {m.titulo.etiqueta && <div style={{display: 'inline-block', fontFamily: SANS, fontWeight: 800, fontSize: 38, color: C.blanco, background: C.azul, borderRadius: 16, padding: '12px 26px', marginBottom: 28, transform: `scale(${spring({frame: f, fps, config: {damping: 10, stiffness: 160}})}) rotate(-2deg)`}}>{m.titulo.etiqueta}</div>}
            <div style={{fontFamily: SANS, fontWeight: 900, fontSize: 112, lineHeight: 1.0, color: C.blanco, textShadow: '0 6px 30px rgba(0,0,0,0.45)', display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 24px'}}>
              {m.titulo.texto.split(' ').map((p, i) => {const s = spring({frame: f - 3 - i * 3, fps, config: {damping: 12, stiffness: 170}}); return <span key={i} style={{display: 'inline-block', opacity: Math.min(1, s * 1.5), transform: `translateY(${50 * (1 - s)}px)`}}>{p}</span>;})}
            </div>
          </div>
        </AbsoluteFill>
      )}

      {golpes.map((g, i) => <GolpeTxt key={i} g={g} t={t} arriba={esc.modo === 'tarjeta' ? 1100 : 560} />)}

      {!enTitulo && <Subtitulo m={m} t={t} arriba={esc.modo === 'tarjeta' ? 1700 : 1460} />}

      {/* Barra de progreso arriba */}
      <div style={{position: 'absolute', top: 0, left: 0, height: 10, width: `${(t / m.duracion) * 100}%`, background: C.azul}} />
    </AbsoluteFill>
  );
};

const TarjetaViva: React.FC<{d: TarjetaDef; t0: number}> = ({d, t0}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <Tarjeta d={d} t={f / fps} t0={t0} />;
};

// Envuelve la tarjeta: entra deslizando desde la derecha con rebote
const Entrada: React.FC<{children: React.ReactNode; arriba: number}> = ({children, arriba}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 14, stiffness: 140}});
  return <div style={{position: 'absolute', left: 60, top: arriba, width: 960, transform: `translateX(${interpolate(s, [0, 1], [900, 0])}px) rotate(${interpolate(s, [0, 1], [6, 0])}deg)`, opacity: Math.min(1, s * 2)}}>{children}</div>;
};

const Root: React.FC = () => (
  <Composition id="Reel" component={Reel as any} fps={30} width={1080} height={1920}
    defaultProps={{duracion: 5, titulo: {texto: '', inicio: 0, fin: 1}, pasos: [], palabras: []}}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil((props as Montaje).duracion * 30)})} />
);
registerRoot(Root);
