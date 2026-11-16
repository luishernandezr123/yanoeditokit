#!/usr/bin/env python3
"""Agente CapCut · crea un borrador (proyecto) NUEVO y editable de CapCut a partir de medios terminados.

Uso:
  python3 herramientas/capcut_borrador.py --nombre "Mi video - CapCut" \\
      --video videos/<nombre>/exportados/<video>.mp4 \\
      --audio voz=<voz.wav> --audio musica=<musica.wav> --audio efectos=<efectos.wav> [--instalar]

Sin --instalar:
  arma el borrador en <carpeta del video>/capcut/<nombre>/ (junto al video), lo comprueba
  y deja el informe en <carpeta del video>/capcut/<nombre>.control.json. No toca CapCut.
Con --instalar (además):
  con CapCut cerrado y sin archivos .locked, copia esa carpeta a la carpeta de borradores
  de CapCut (ver carpeta_capcut), respalda root_meta_info.json como
  root_meta_info.json.bak-<fecha> y añade la entrada para que CapCut lo liste en Inicio.
  Se niega si ya existe una carpeta o entrada con ese nombre. Si esa carpeta no tiene
  root_meta_info.json, deja el borrador copiado, avisa y no inventa el registro.

Contenido del borrador:
  lienzo 9:16 (1080x1920 lógicos, convención de la semilla);
  pista 1 «video»: el video completo, volumen 0 (se espera sin audio);
  una pista de audio por cada --audio (nombre = clave: voz, musica, efectos), completa, volumen 1.0.
  Los medios se COPIAN a <borrador>/Resources/ y se referencian con el prefijo
  ##_draftpath_placeholder_…##/Resources/… como hacen los borradores de CapCut.

De dónde sale el formato (no se inventa): plantillas/capcut-molde/ del kit, sacado de
borradores reales guardados por CapCut (formato 191.0.0, app 9.7.1 en Mac) y limpiado de
rutas, nombres, portadas, identificadores del equipo e IDs de muestra:
  - borrador/: esqueleto vacío (draft_info, draft_meta_info, Timelines/project.json,
    timeline_layout, draft_virtual_store, draft_settings) y archivos auxiliares vacíos
    (attachment_*, common_attachment, Timelines/linea/common_attachment).
  - pistas.json: material y segmento de video y de audio, con los materiales auxiliares que
    cada segmento referencia (speeds, placeholder_infos, canvases, sound_channel_mappings…).
  - entrada_registro.json: entrada modelo de root_meta_info.json.
Todos los IDs y rutas se generan en cada ejecución.
Solo biblioteca estándar de Python 3.9+, ffprobe y ffmpeg.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from fractions import Fraction
from pathlib import Path

# ── Rutas del kit ────────────────────────────────────────────────────────────
MOLDE = Path(__file__).resolve().parent.parent / 'plantillas' / 'capcut-molde'
ESQUELETO = MOLDE / 'borrador'                  # borrador vacío + auxiliares
MOLDE_PISTAS = MOLDE / 'pistas.json'            # material y segmento de video y de audio
MOLDE_ENTRADA = MOLDE / 'entrada_registro.json'  # entrada modelo de root_meta_info.json


def carpeta_capcut():
    """Carpeta de borradores de CapCut según el sistema (o None si no se conoce)."""
    if sys.platform == 'darwin':
        return Path.home() / 'Movies/CapCut/User Data/Projects/com.lveditor.draft'
    if os.name == 'nt':
        # Windows: ruta habitual de CapCut para escritorio. NO PROBADO todavía en Windows.
        base = os.environ.get('LOCALAPPDATA')
        return Path(base) / 'CapCut' / 'User Data' / 'Projects' / 'com.lveditor.draft' if base else None
    return None


def buscar_programa(nombre, junto_a=None):
    """Busca ffmpeg/ffprobe: variable FFMPEG/FFPROBE si existe, junto a ffmpeg, en el PATH y en
    las rutas comunes, como herramientas/cortar.py."""
    candidatos = []
    if os.environ.get(nombre.upper()):
        candidatos.append(Path(os.environ[nombre.upper()]).expanduser())
    if junto_a:
        candidatos.append(Path(junto_a).with_name(Path(junto_a).name.replace('ffmpeg', nombre)))
    encontrado = shutil.which(nombre)
    if encontrado:
        candidatos.append(Path(encontrado))
    candidatos += [Path(d) / nombre for d in ('/opt/homebrew/bin', '/usr/local/bin', '/usr/bin')]
    candidatos += [Path.home() / 'bin' / nombre]
    for c in candidatos:
        if c.is_file():
            return c
    return None


FFMPEG = buscar_programa('ffmpeg')
FFPROBE = buscar_programa('ffprobe', junto_a=FFMPEG)

PREFIJO = '##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/'
VERSION = '191.0.0'
LIENZO = (1080, 1920)
FPS_VALIDOS = (24, 25, 30, 50, 60)
UUID_RE = re.compile(r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}')
UUID_PREFIJO = UUID_RE.search(PREFIJO).group(0).upper()

GENERADOS = set()  # todos los IDs creados en esta ejecución (para detectar referencias viejas)


# ── Utilidades ───────────────────────────────────────────────────────────────
class Rechazo(Exception):
    """Condición que impide continuar sin riesgo."""


def exigir(condicion, mensaje):
    if not condicion:
        raise Rechazo(mensaje)


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding='utf-8'))


def escribir(ruta, obj):
    """JSON compacto en UTF-8 sin escapar, como lo guarda CapCut; escritura atómica."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + '.nuevo')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    os.replace(tmp, ruta)


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(1024 ** 2), b''):
            h.update(bloque)
    return h.hexdigest()


def uid():
    nuevo = str(uuid.uuid4()).upper()
    GENERADOS.add(nuevo)
    return nuevo


def ahora_us():
    return time.time_ns() // 1000


def sello():
    return time.strftime('%Y%m%d-%H%M%S')


# ── Medios ───────────────────────────────────────────────────────────────────
def sondear(ruta):
    salida = subprocess.check_output([str(FFPROBE), '-v', 'error', '-show_streams', '-show_format',
                                      '-of', 'json', str(ruta)], text=True)
    return json.loads(salida)


def duracion_us(stream, formato):
    """Duración exacta en microsegundos: duration_ts·time_base, luego duration del stream o del formato."""
    if stream.get('duration_ts') not in (None, 'N/A') and stream.get('time_base'):
        return round(int(stream['duration_ts']) * Fraction(stream['time_base']) * 1_000_000)
    for fuente in (stream, formato):
        if fuente.get('duration') not in (None, 'N/A'):
            return round(Fraction(fuente['duration']) * 1_000_000)
    raise Rechazo('No se pudo medir la duración')


def medir_video(ruta, avisos):
    info = sondear(ruta)
    videos = [s for s in info['streams'] if s['codec_type'] == 'video'
              and not s.get('disposition', {}).get('attached_pic')]
    exigir(len(videos) == 1, f'{ruta.name}: se esperaba exactamente una pista de video')
    v = videos[0]
    tiene_audio = any(s['codec_type'] == 'audio' for s in info['streams'])
    if tiene_audio:
        avisos.append(f'{ruta.name} trae audio; queda en volumen 0 dentro del borrador')
    tasa = Fraction(v['r_frame_rate'])
    cuadros = int(v['nb_frames']) if str(v.get('nb_frames', '')).isdigit() else None
    if cuadros and tasa:
        dur = round(cuadros * 1_000_000 / tasa)
    else:
        dur = duracion_us(v, info['format'])
    w, h = int(v['width']), int(v['height'])
    rot = int(v.get('tags', {}).get('rotate', 0) or 0)
    for d in v.get('side_data_list', []):
        if 'rotation' in d:
            rot = int(d['rotation'])
    if rot % 180:
        w, h = h, w
    if w * LIENZO[1] != h * LIENZO[0]:
        avisos.append(f'{ruta.name} mide {w}x{h}, no es 9:16; CapCut lo encajará en el lienzo 9:16')
    fps = round(tasa) if tasa else 30
    if fps not in FPS_VALIDOS or abs(tasa - fps) > Fraction(1, 100):
        avisos.append(f'{ruta.name}: {float(tasa):.3f} fps; el proyecto queda a 30 fps')
        fps = 30
    return dict(duracion=dur, ancho=w, alto=h, fps=fps, cuadros=cuadros, tiene_audio=tiene_audio)


def medir_audio(ruta):
    info = sondear(ruta)
    audios = [s for s in info['streams'] if s['codec_type'] == 'audio']
    exigir(len(audios) >= 1, f'{ruta.name}: no tiene pista de audio')
    a = audios[0]
    return dict(duracion=duracion_us(a, info['format']), muestreo=int(a.get('sample_rate', 0)),
                canales=int(a.get('channels', 0)), codec=a.get('codec_name'))


def portada(video, destino, duracion):
    segundo = min(1.0, duracion / 2_000_000)
    subprocess.run([str(FFMPEG), '-nostdin', '-y', '-v', 'error', '-ss', f'{segundo:.3f}', '-i', str(video),
                    '-frames:v', '1', '-vf', 'scale=540:-2', '-q:v', '2', '-update', '1', str(destino)],
                   check=True)
    exigir(destino.is_file() and destino.stat().st_size > 0, 'No se generó la portada')


# ── Argumentos ───────────────────────────────────────────────────────────────
def validar_nombre(nombre):
    nombre = nombre.strip()
    exigir(nombre and len(nombre) <= 120, 'El nombre está vacío o es demasiado largo')
    exigir(not nombre.startswith('.') and not any(c in nombre for c in '/:\\') and nombre.isprintable(),
           'El nombre no puede empezar por punto ni contener / : \\ o caracteres de control')
    return nombre


def leer_audios(valores):
    pistas = []
    for valor in valores:
        exigir('=' in valor, f'--audio debe ser clave=ruta (recibido: {valor})')
        clave, ruta = valor.split('=', 1)
        clave = clave.strip()
        exigir(re.fullmatch(r'[a-z0-9_-]{1,40}', clave) and clave != 'video',
               f'Clave de audio no válida: {clave!r} (minúsculas, números, - o _; no «video»)')
        exigir(clave not in {p['clave'] for p in pistas}, f'Clave de audio repetida: {clave}')
        ruta = Path(ruta).expanduser().resolve()
        exigir(ruta.is_file(), f'No existe el audio {ruta}')
        pistas.append(dict(clave=clave, origen=ruta))
    return pistas


# ── Plantillas nativas ───────────────────────────────────────────────────────
def indice_materiales(doc):
    indice = {}
    for tipo, lista in doc['materials'].items():
        if isinstance(lista, list):
            for m in lista:
                if isinstance(m, dict) and 'id' in m:
                    indice[m['id']] = (tipo, m)
    return indice


MOLDE_ARCHIVOS = ('draft_info.json', 'draft_meta_info.json', 'draft_settings', 'draft_virtual_store.json',
                  'timeline_layout.json', 'Timelines/project.json', 'attachment_editing.json',
                  'attachment_pc_common.json', 'draft_agency_config.json', 'draft_biz_config.json',
                  'performance_opt_info.json', 'common_attachment', 'Timelines/linea/common_attachment')


def plantillas():
    for rel in MOLDE_ARCHIVOS:
        exigir((ESQUELETO / rel).exists(), f'Falta en el molde del kit: {ESQUELETO / rel}')
    for ruta in (MOLDE_PISTAS, MOLDE_ENTRADA):
        exigir(ruta.is_file(), f'Falta en el molde del kit: {ruta}')
    n = leer(ESQUELETO / 'draft_info.json')
    pistas = leer(MOLDE_PISTAS)
    exigir(n['new_version'] == pistas['version_capcut'] == VERSION,
           f'Versiones de borrador divergentes en el molde (se esperaba {VERSION})')
    for clave in ('video', 'audio'):
        for extra in pistas[clave]['extras']:
            exigir(extra['lista'] in n['materials'], f'El esqueleto no tiene la lista {extra["lista"]}')
    return dict(
        semilla=n,
        material_video=pistas['video']['material'], segmento_video=pistas['video']['segmento'],
        extras_video=pistas['video']['extras'],
        material_audio=pistas['audio']['material'], segmento_audio=pistas['audio']['segmento'],
        extras_audio=pistas['audio']['extras'])


def clonar_refs(n, extras):
    """Copia cada material auxiliar que el segmento necesita, con ID nuevo."""
    refs = []
    for extra in extras:
        tipo, modelo = extra['lista'], extra['material']
        exigir(tipo in n['materials'], f'El esqueleto no tiene la lista {tipo}')
        m = copy.deepcopy(modelo)
        m['id'] = uid()
        if tipo == 'speeds':
            m.update(speed=1.0, mode=0, curve_speed=None)
        n['materials'][tipo].append(m)
        refs.append(m['id'])
    return refs


# ── Construcción ─────────────────────────────────────────────────────────────
def construir(nombre, video, pistas, avisos):
    t = plantillas()
    n = copy.deepcopy(t['semilla'])
    meta = leer(ESQUELETO / 'draft_meta_info.json')
    proyecto = leer(ESQUELETO / 'Timelines/project.json')
    disposicion = leer(ESQUELETO / 'timeline_layout.json')
    virtual = leer(ESQUELETO / 'draft_virtual_store.json')

    mv = medir_video(video, avisos)
    for p in pistas:
        p.update(medir_audio(p['origen']))
        dif = abs(p['duracion'] - mv['duracion'])
        if dif > 1_000_000 / mv['fps']:
            avisos.append(f'audio {p["clave"]} dura {p["duracion"] / 1e6:.3f} s y el video '
                          f'{mv["duracion"] / 1e6:.3f} s (diferencia {dif / 1e6:.3f} s)')
    total = max([mv['duracion']] + [p['duracion'] for p in pistas])

    carpeta = video.parent / 'capcut'
    final = carpeta / nombre
    trabajo = carpeta / f'.{nombre}.construyendo-{sello()}'
    exigir(not trabajo.exists(), f'Ya existe {trabajo}')
    res = trabajo / 'Resources'
    res.mkdir(parents=True)

    try:
        return _construir(nombre, video, pistas, avisos, t, n, meta, proyecto, disposicion, virtual,
                          mv, total, carpeta, final, trabajo, res)
    except BaseException:
        if trabajo.exists():  # solo la carpeta temporal creada en esta ejecución
            shutil.rmtree(trabajo)
        raise


def _construir(nombre, video, pistas, avisos, t, n, meta, proyecto, disposicion, virtual,
               mv, total, carpeta, final, trabajo, res):
    timeline_id, proyecto_id, draft_id = uid(), uid(), uid()
    ahora = ahora_us()

    n.update(id=timeline_id, name=nombre, duration=total, fps=float(mv['fps']), path=PREFIJO[:-1],
             create_time=ahora // 1_000_000, update_time=ahora // 1_000_000, tracks=[],
             materials={k: [] for k in n['materials']}, group_container=None,
             keyframes={k: [] for k in n['keyframes']}, keyframe_graph_list=[], relationships=[],
             cover=None, retouch_cover=None, static_cover_image_path='')
    n['canvas_config'].update(width=LIENZO[0], height=LIENZO[1], ratio='9:16')
    n['config'].update(maintrack_adsorb=False, video_mute=False, export_range=None)

    registro, recursos = [], []

    def copiar(origen, nombre_archivo):
        destino = res / nombre_archivo
        exigir(not destino.exists(), f'Recurso repetido: {nombre_archivo}')
        shutil.copy2(origen, destino)
        huella = sha256(destino)
        exigir(huella == sha256(origen), f'La copia de {origen.name} no coincide')
        rel = destino.relative_to(trabajo).as_posix()
        recursos.append(dict(ruta=rel, origen=str(origen), bytes=destino.stat().st_size, sha256=huella))
        return rel

    def registrar(lid, rel, duracion, metetype, ancho=0, alto=0):
        segundos = ahora // 1_000_000
        registro.append(dict(ai_group_type='', create_time=segundos, duration=duracion, enter_from=0,
                             extra_info=Path(rel).name, file_Path='./' + rel, height=alto, id=lid,
                             import_time=segundos, import_time_ms=ahora, item_source=1,
                             material_color_tag='', md5='', metetype=metetype,
                             roughcut_time_range=dict(duration=duracion, start=0),
                             sub_time_range=dict(duration=-1, start=-1), type=0, width=ancho))

    # Pista 1 · video completo, volumen 0 (material y segmento de video del molde).
    rel = copiar(video, f'video-{video.name}')
    mid, lid = uid(), uid()
    m = copy.deepcopy(t['material_video'])
    m.update(id=mid, unique_id=uid(), local_material_id=lid, material_id=mid, local_id='', media_path='',
             path=PREFIJO + rel, material_name=video.name, duration=mv['duracion'], width=mv['ancho'],
             height=mv['alto'], type='video', has_audio=mv['tiene_audio'], crop_ratio='free',
             crop_scale=1.0, origin_material_id='')
    m['video_algorithm']['time_range'] = None
    m['crop'] = dict(upper_left_x=0.0, upper_left_y=0.0, upper_right_x=1.0, upper_right_y=0.0,
                     lower_left_x=0.0, lower_left_y=1.0, lower_right_x=1.0, lower_right_y=1.0)
    n['materials']['videos'].append(m)
    registrar(lid, rel, mv['duracion'], 'video', mv['ancho'], mv['alto'])
    seg = copy.deepcopy(t['segmento_video'])
    seg.update(id=uid(), material_id=mid, extra_material_refs=clonar_refs(n, t['extras_video']),
               speed=1.0, source_timerange=dict(start=0, duration=mv['duracion']),
               target_timerange=dict(start=0, duration=mv['duracion']), common_keyframes=[], keyframe_refs=[],
               volume=0.0, last_nonzero_volume=1.0, track_render_index=0, render_index=0, visible=True,
               enable_adjust=False, enable_lut=False, enable_hsl=False, enable_color_curves=False,
               enable_hsl_curves=False, enable_color_wheels=False, enable_smart_color_adjust=False,
               enable_color_match_adjust=False, enable_color_correct_adjust=False,
               enable_adjust_mask=False, enable_color_adjust_pro=False)
    seg['clip'] = dict(alpha=1.0, flip=dict(horizontal=False, vertical=False), rotation=0.0,
                       scale=dict(x=1.0, y=1.0), transform=dict(x=0.0, y=0.0))
    seg['uniform_scale'] = dict(on=True, value=1.0)
    n['tracks'].append(dict(id=uid(), type='video', attribute=0, flag=0, name='video',
                            is_default_name=False, segments=[seg]))

    # Pistas de audio · una por clave, completas, volumen 1.0 (material y segmento de audio del molde).
    for p in pistas:
        rel = copiar(p['origen'], f'{p["clave"]}-{p["origen"].name}')
        m = copy.deepcopy(t['material_audio'])
        m.update(id=uid(), unique_id=uid(), local_material_id=uid(), name=p['clave'], path=PREFIJO + rel,
                 duration=p['duracion'], type='extract_music', wave_points=[], music_id='')
        n['materials']['audios'].append(m)
        registrar(m['local_material_id'], rel, p['duracion'], 'music')
        seg = copy.deepcopy(t['segmento_audio'])
        seg.update(id=uid(), material_id=m['id'],
                   extra_material_refs=clonar_refs(n, t['extras_audio']),
                   speed=1.0, source_timerange=dict(start=0, duration=p['duracion']),
                   target_timerange=dict(start=0, duration=p['duracion']), common_keyframes=[],
                   keyframe_refs=[], volume=1.0, last_nonzero_volume=1.0, render_index=0,
                   track_render_index=len(n['tracks']), visible=True)
        n['tracks'].append(dict(id=uid(), type='audio', attribute=0, flag=0, name=p['clave'],
                                is_default_name=False, segments=[seg]))

    # Portada desde el primer segundo del video.
    tl = trabajo / 'Timelines' / timeline_id
    tl.mkdir(parents=True)
    portada(video, trabajo / 'draft_cover.jpg', mv['duracion'])
    shutil.copy2(trabajo / 'draft_cover.jpg', tl / 'draft_cover.jpg')

    # Metadatos (draft_meta_info), proyecto, disposición y almacén virtual.
    meta.update(draft_id=draft_id, draft_name=nombre, tm_duration=total, tm_draft_create=ahora,
                tm_draft_modified=ahora, draft_fold_path=final.as_posix(), draft_root_path=carpeta.as_posix(),
                draft_cover='draft_cover.jpg', draft_timeline_materials_size_=sum(r['bytes'] for r in recursos),
                draft_materials_copied_info=[], draft_segment_extra_info=[])
    meta.pop('draft_json_file', None)
    for grupo in meta['draft_materials']:
        grupo['value'] = registro if grupo['type'] == 0 else []
    proyecto.update(id=proyecto_id, main_timeline_id=timeline_id, create_time=ahora, update_time=ahora,
                    timelines=[dict(id=timeline_id, is_marked_delete=False, name='Línea de tiempo 01',
                                    create_time=ahora, update_time=ahora)])
    exigir(len(disposicion['dockItems']) == 1, 'El molde debe tener una sola línea de tiempo en timeline_layout')
    disposicion['dockItems'][0]['timelineIds'] = [timeline_id]
    for grupo in virtual['draft_virtual_store']:
        if grupo['type'] == 0:  # solo la entrada raíz vacía; se quitan carpetas de la semilla
            grupo['value'] = [v for v in grupo['value'] if v.get('id') == ''][:1]
        elif grupo['type'] == 1:
            grupo['value'] = [dict(child_id=r['id'], parent_id='') for r in registro]
        else:
            grupo['value'] = []

    for archivo in ('draft_info.json', 'draft_info.json.bak', 'template-2.tmp'):
        escribir(trabajo / archivo, n)
    escribir(tl / 'draft_info.json', n)
    escribir(tl / 'draft_info.json.bak', n)
    escribir(trabajo / 'Timelines/project.json', proyecto)
    escribir(trabajo / 'Timelines/project.json.bak', proyecto)
    escribir(trabajo / 'timeline_layout.json', disposicion)
    escribir(trabajo / 'draft_meta_info.json', meta)
    escribir(trabajo / 'draft_virtual_store.json', virtual)

    # draft_settings con las horas de ahora, mismo formato que el molde.
    lineas = []
    for linea in (ESQUELETO / 'draft_settings').read_text(encoding='utf-8').splitlines():
        clave = linea.split('=', 1)[0]
        if clave in ('draft_create_time', 'draft_last_edit_time'):
            linea = f'{clave}={ahora // 1_000_000}'
        elif clave in ('real_edit_keys', 'real_edit_seconds'):
            linea = f'{clave}=0'
        lineas.append(linea)
    (trabajo / 'draft_settings').write_text('\n'.join(lineas) + '\n', encoding='utf-8')

    # Archivos auxiliares vacíos que CapCut crea en todo borrador nuevo (sin IDs).
    vacio_tl = ESQUELETO / 'Timelines/linea'
    for origen, destino in [
        (ESQUELETO / 'attachment_editing.json', 'attachment_editing.json'),
        (ESQUELETO / 'attachment_editing.json', f'Timelines/{timeline_id}/attachment_editing.json'),
        (ESQUELETO / 'attachment_pc_common.json', 'attachment_pc_common.json'),
        (ESQUELETO / 'attachment_pc_common.json', f'Timelines/{timeline_id}/attachment_pc_common.json'),
        (ESQUELETO / 'draft_agency_config.json', 'draft_agency_config.json'),
        (ESQUELETO / 'draft_biz_config.json', 'draft_biz_config.json'),
        (ESQUELETO / 'performance_opt_info.json', 'performance_opt_info.json'),
    ] + [(f, f'common_attachment/{f.name}') for f in sorted((ESQUELETO / 'common_attachment').glob('*.json'))] \
      + [(f, f'Timelines/{timeline_id}/common_attachment/{f.name}')
         for f in sorted((vacio_tl / 'common_attachment').glob('*.json'))]:
        (trabajo / destino).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, trabajo / destino)
    for vacia in ('adjust_mask', 'matting', 'qr_upload', 'smart_crop', 'subdraft'):
        (trabajo / vacia).mkdir(exist_ok=True)

    esperado = dict(video=mv, pistas=[{k: p[k] for k in ('clave', 'duracion')} for p in pistas],
                    total=total, recursos=recursos)
    verificar(trabajo, esperado, final)  # meta ya apunta a la carpeta definitiva

    # Si ya había un borrador local con ese nombre, se aparta (nunca se borra).
    apartado = None
    if final.exists():
        apartado = carpeta / f'{nombre}.anterior-{sello()}'
        os.rename(final, apartado)
        avisos.append(f'el borrador local anterior se apartó en {apartado}')
    os.rename(trabajo, final)
    verificar(final, esperado, final)
    return final, esperado, dict(timeline=timeline_id, proyecto=proyecto_id, borrador=draft_id), apartado


# ── Verificación ─────────────────────────────────────────────────────────────
def verificar(borrador, esperado, carpeta_meta):
    """Comprueba JSON, IDs, duraciones, rutas y huellas. Lanza Rechazo si algo no cuadra."""
    for f in borrador.rglob('*'):
        if f.is_file() and f.suffix in ('.json', '.tmp', '.bak') and 'Resources' not in f.parts:
            if f.stat().st_size:
                json.loads(f.read_text(encoding='utf-8'))  # todos los JSON cargan
    n = leer(borrador / 'draft_info.json')
    meta = leer(borrador / 'draft_meta_info.json')
    proyecto = leer(borrador / 'Timelines/project.json')
    disposicion = leer(borrador / 'timeline_layout.json')
    virtual = leer(borrador / 'draft_virtual_store.json')
    tl = borrador / 'Timelines' / n['id']
    for copia in (borrador / 'draft_info.json.bak', borrador / 'template-2.tmp', tl / 'draft_info.json',
                  tl / 'draft_info.json.bak'):
        exigir(leer(copia) == n, f'Copia divergente: {copia.name}')
    exigir(n['new_version'] == VERSION, 'Versión inesperada')
    exigir(n['id'] == proyecto['main_timeline_id'] == proyecto['timelines'][0]['id']
           == disposicion['dockItems'][0]['timelineIds'][0], 'Línea de tiempo incoherente')
    exigir(len({n['id'], meta['draft_id'], proyecto['id']}) == 3, 'IDs principales repetidos')
    exigir((n['canvas_config']['width'], n['canvas_config']['height'], n['canvas_config']['ratio'])
           == (LIENZO[0], LIENZO[1], '9:16'), 'Lienzo distinto de 9:16 1080x1920')
    exigir(n['duration'] == meta['tm_duration'] == esperado['total'], 'Duración total divergente')
    exigir(meta['draft_name'] == n['name'] and Path(meta['draft_fold_path']) == carpeta_meta,
           'draft_meta_info no apunta a esta carpeta')

    # IDs únicos en pistas, segmentos y materiales.
    ids = [n['id']]
    for tr in n['tracks']:
        ids.append(tr['id'])
        ids += [s['id'] for s in tr['segments']]
    for lista in n['materials'].values():
        ids += [m['id'] for m in lista if isinstance(m, dict) and 'id' in m]
    exigir(all(ids) and len(ids) == len(set(ids)), 'Hay IDs vacíos o repetidos en el borrador')
    indice = indice_materiales(n)

    # Pistas: 1 video + audios en orden, cada una completa.
    tipos = [(tr['type'], tr['name']) for tr in n['tracks']]
    exigir(tipos == [('video', 'video')] + [('audio', p['clave']) for p in esperado['pistas']],
           f'Pistas inesperadas: {tipos}')
    usados = []
    duraciones = [esperado['video']['duracion']] + [p['duracion'] for p in esperado['pistas']]
    for i, (tr, dur) in enumerate(zip(n['tracks'], duraciones)):
        exigir(len(tr['segments']) == 1, f'La pista {tr["name"]} debe tener un segmento')
        s = tr['segments'][0]
        tipo_lista, m = indice[s['material_id']]
        exigir(tipo_lista == ('videos' if tr['type'] == 'video' else 'audios'), 'Material en lista equivocada')
        exigir(s['target_timerange'] == {'start': 0, 'duration': dur} == s['source_timerange'] and
               m['duration'] == dur, f'Pista {tr["name"]}: no ocupa la duración completa del medio')
        exigir(s['volume'] == (0.0 if tr['type'] == 'video' else 1.0), f'Pista {tr["name"]}: volumen inesperado')
        exigir(s['track_render_index'] == i, 'Orden de render incoherente')
        for ref in s['extra_material_refs']:
            exigir(ref in indice, f'Referencia extra sin material: {ref}')
        usados += s['extra_material_refs'] + [s['material_id']]
        exigir(m['path'].startswith(PREFIJO), 'Ruta de material no portable')
        rel = m['path'][len(PREFIJO):]
        archivo = (borrador / rel).resolve()
        exigir(archivo.is_file() and archivo.is_relative_to(borrador.resolve() / 'Resources'),
               f'Falta el medio {rel} dentro de Resources')
    exigir(len(usados) == len(set(usados)) == len(indice), 'Materiales sin usar o compartidos entre segmentos')

    # Huellas de los recursos copiados y registro de medios.
    for r in esperado['recursos']:
        f = borrador / r['ruta']
        exigir(f.is_file() and f.stat().st_size == r['bytes'] and sha256(f) == r['sha256'],
               f'Recurso alterado: {r["ruta"]}')
    reg = [v for g in meta['draft_materials'] if g['type'] == 0 for v in g['value']]
    exigir(len(reg) == len(esperado['recursos']), 'Registro de medios incompleto')
    for v in reg:
        exigir((borrador / v['file_Path'][2:]).is_file(), f'Registro apunta a un archivo ausente: {v["file_Path"]}')
    hijos = [v['child_id'] for g in virtual['draft_virtual_store'] if g['type'] == 1 for v in g['value']]
    exigir(sorted(hijos) == sorted(v['id'] for v in reg), 'Almacén virtual divergente del registro')
    exigir((borrador / meta['draft_cover']).is_file(), 'Falta la portada')

    # Ningún UUID heredado del molde: todos se generaron en esta ejecución.
    rutas_propias = sorted({str(borrador), str(carpeta_meta), borrador.as_posix(), carpeta_meta.as_posix(),
                            meta['draft_fold_path'], meta['draft_root_path']}, key=len, reverse=True)
    for f in borrador.rglob('*'):
        if f.is_file() and f.suffix in ('.json', '.tmp', '.bak') and 'Resources' not in f.parts:
            texto = f.read_text(encoding='utf-8')
            for ruta in rutas_propias:  # las rutas de carpeta pueden contener UUID ajenos al formato
                texto = texto.replace(ruta, '')
            viejos = {u.upper() for u in UUID_RE.findall(texto)} - GENERADOS - {UUID_PREFIJO}
            exigir(not viejos, f'{f.relative_to(borrador)} conserva IDs de la muestra: {sorted(viejos)[:3]}')


# ── Instalación en CapCut ───────────────────────────────────────────────────
def capcut_abierto():
    """Procesos de CapCut (incluidos ayudantes). Excluye este script, cuyo nombre contiene «capcut»."""
    encontrados = []
    if os.name == 'nt':  # Windows (no probado): lista de tareas en CSV
        r = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True)
        for linea in r.stdout.splitlines():
            proceso = linea.split('","')[0].strip('"')
            if 'capcut' in proceso.lower():
                encontrados.append(linea[:80])
        return encontrados
    r = subprocess.run(['pgrep', '-x', 'CapCut'], capture_output=True, text=True)
    encontrados += r.stdout.split()
    propios = {str(os.getpid()), str(os.getppid())}
    r = subprocess.run(['pgrep', '-if', 'capcut'], capture_output=True, text=True)
    for pid in r.stdout.split():
        if pid in propios:
            continue
        cmd = subprocess.run(['ps', '-o', 'command=', '-p', pid], capture_output=True, text=True).stdout
        if 'capcut_borrador' in cmd or 'pgrep' in cmd:
            continue
        encontrados.append(f'{pid} {cmd.strip()[:80]}')
    return encontrados


def bloqueos(raiz):
    hallados = []
    for actual, carpetas, archivos in os.walk(raiz):
        carpetas[:] = [c for c in carpetas if c != 'Resources']
        hallados += [str(Path(actual) / a) for a in archivos if a.endswith('.locked')]
    return hallados


def comprobar_instalacion(nombre, raiz):
    """Devuelve (carpeta destino, hay registro). Se niega ante cualquier riesgo."""
    exigir(raiz is not None, 'No se conoce la carpeta de borradores de CapCut en este sistema; '
                             'indícala con --carpeta-capcut')
    exigir(raiz.is_dir(), f'No se encuentra la carpeta de borradores de CapCut: {raiz}. '
                          'Abre CapCut una vez y ciérralo, o indícala con --carpeta-capcut')
    meta_raiz = raiz / 'root_meta_info.json'
    abiertos = capcut_abierto()
    exigir(not abiertos, f'CapCut está abierto; ciérralo por completo y repite ({abiertos[:3]})')
    locks = bloqueos(raiz)
    exigir(not locks, f'Hay archivos .locked en los borradores; cierra CapCut ({locks[:3]})')
    destino = raiz / nombre
    exigir(not destino.exists(), f'Ya existe una carpeta con ese nombre en CapCut: {destino}')
    hay_registro = meta_raiz.is_file()
    if hay_registro:
        for e in leer(meta_raiz)['all_draft_store']:
            exigir(e.get('draft_name') != nombre and e.get('draft_fold_path') not in (str(destino), destino.as_posix()),
                   f'root_meta_info.json ya tiene un borrador llamado «{nombre}»')
    return destino, hay_registro


def registrados(meta_raiz):
    return leer(meta_raiz)['all_draft_store'] if meta_raiz.is_file() else []


def instalar(local, nombre, esperado, raiz, avisos):
    destino, hay_registro = comprobar_instalacion(nombre, raiz)
    meta_raiz = raiz / 'root_meta_info.json'
    temporal = raiz / f'.{nombre}.instalando-{sello()}'
    exigir(not temporal.exists(), f'Ya existe {temporal}')
    shutil.copytree(local, temporal)
    respaldo = None
    try:
        meta = leer(temporal / 'draft_meta_info.json')
        meta.update(draft_fold_path=destino.as_posix(), draft_root_path=raiz.as_posix())
        escribir(temporal / 'draft_meta_info.json', meta)
        # Última comprobación justo antes de tocar la carpeta de CapCut.
        exigir(not capcut_abierto() and not destino.exists(), 'CapCut se abrió o apareció la carpeta durante la copia')
        os.rename(temporal, destino)
        verificar(destino, esperado, destino)

        if not hay_registro:
            avisos.append(f'{raiz} no tiene root_meta_info.json: el borrador quedó copiado en {destino}, '
                          'pero no se creó ningún registro. Si CapCut no lo lista en Inicio, ábrelo desde '
                          'esa carpeta o avisa; el registro no se inventa.')
            return dict(carpeta=str(destino), registrado=False, respaldo_root_meta=None,
                        draft_id=meta['draft_id'])

        respaldo = raiz / f'root_meta_info.json.bak-{sello()}'
        exigir(not respaldo.exists(), f'Ya existe {respaldo}')
        shutil.copy2(meta_raiz, respaldo)
        exigir(sha256(respaldo) == sha256(meta_raiz), 'El respaldo de root_meta_info.json no coincide')
        registro = leer(meta_raiz)
        entrada = copy.deepcopy(leer(MOLDE_ENTRADA))
        ahora = ahora_us()
        entrada.update(draft_cover=(destino / 'draft_cover.jpg').as_posix(), draft_fold_path=destino.as_posix(),
                       draft_id=meta['draft_id'], draft_json_file=(destino / 'draft_info.json').as_posix(),
                       draft_name=nombre, draft_root_path=raiz.as_posix(), tm_draft_create=ahora,
                       tm_draft_modified=ahora, tm_draft_removed=0, tm_duration=esperado['total'])
        registro['all_draft_store'].insert(0, entrada)  # el más reciente primero, como lo ordena CapCut
        if isinstance(registro.get('draft_ids'), list):
            registro['draft_ids'] = list(dict.fromkeys(registro['draft_ids'] + [meta['draft_id']]))
        escribir(meta_raiz, registro)
        releido = leer(meta_raiz)
        exigir(sum(e.get('draft_id') == meta['draft_id'] for e in releido['all_draft_store']) == 1,
               'La entrada no quedó registrada una sola vez')
    except BaseException:
        # Solo se retira la copia creada en esta ejecución; el registro no se tocó o ya tiene respaldo.
        for carpeta in (temporal, destino):
            if carpeta.exists() and not any(e.get('draft_fold_path') in (str(carpeta), carpeta.as_posix())
                                            for e in registrados(meta_raiz)):
                shutil.rmtree(carpeta)
        raise
    return dict(carpeta=str(destino), registrado=True, respaldo_root_meta=str(respaldo),
                draft_id=meta['draft_id'], entradas_registro=len(releido['all_draft_store']))


# ── Principal ────────────────────────────────────────────────────────────────
def principal(argv=None):
    parser = argparse.ArgumentParser(description='Crea un borrador nuevo y editable de CapCut desde medios terminados.')
    parser.add_argument('--nombre', required=True, help='Nombre del proyecto en CapCut')
    parser.add_argument('--video', required=True, type=Path, help='Video final (sin audio)')
    parser.add_argument('--audio', action='append', default=[], metavar='CLAVE=RUTA',
                        help='Pista de audio; repetir por cada una (voz=…, musica=…, efectos=…)')
    parser.add_argument('--instalar', action='store_true', help='Copiar a CapCut y registrarlo en Inicio')
    parser.add_argument('--carpeta-capcut', type=Path, default=None,
                        help='Carpeta de borradores de CapCut (por defecto, la habitual de este sistema)')
    args = parser.parse_args(argv)
    avisos = []
    try:
        exigir(FFPROBE and FFMPEG, 'No se encontró ffmpeg o ffprobe; instálalo (Mac: brew install ffmpeg) '
                                   'o añádelo al PATH')
        nombre = validar_nombre(args.nombre)
        video = args.video.expanduser().resolve()
        exigir(video.is_file(), f'No existe el video {video}')
        pistas = leer_audios(args.audio)
        raiz = args.carpeta_capcut.expanduser().resolve() if args.carpeta_capcut else carpeta_capcut()
        if args.instalar:  # se comprueba antes de construir para no trabajar en balde
            comprobar_instalacion(nombre, raiz)
        local, esperado, ids, apartado = construir(nombre, video, pistas, avisos)
        informe = dict(
            verificado=True, borrador_local=str(local), nombre=nombre, ids=ids,
            lienzo='1080x1920 (9:16)', fps=esperado['video']['fps'],
            duracion_total_s=esperado['total'] / 1e6,
            pistas=[dict(nombre='video', tipo='video', duracion_s=esperado['video']['duracion'] / 1e6, volumen=0.0,
                         medida=f"{esperado['video']['ancho']}x{esperado['video']['alto']}")]
                   + [dict(nombre=p['clave'], tipo='audio', duracion_s=p['duracion'] / 1e6, volumen=1.0)
                      for p in esperado['pistas']],
            recursos=[dict(ruta=r['ruta'], bytes=r['bytes'], sha256=r['sha256']) for r in esperado['recursos']],
            carpeta_capcut=str(raiz) if raiz else None,
            avisos=avisos, instalado=False, abierto_en_capcut=False)
        if args.instalar:
            informe['instalacion'] = instalar(local, nombre, esperado, raiz, avisos)
            informe['instalado'] = True
        elif raiz is None or not (raiz / 'root_meta_info.json').is_file():
            avisos.append(f'no se encontró el registro de CapCut en {raiz}; para --instalar abre CapCut una vez '
                          'o indica --carpeta-capcut')
        escribir_informe = local.parent / f'{nombre}.control.json'
        escribir_informe.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(informe, ensure_ascii=False, indent=2))
        return 0
    except (Rechazo, subprocess.CalledProcessError, OSError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        for aviso in avisos:
            print(f'aviso: {aviso}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(principal())
