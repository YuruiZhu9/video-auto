#!/workspace/venv-uv/bin/python3
"""AI Guitar Tab 扒谱效果测试 v4 — 修正版"""
import sys, os, soundfile as sf

ROOT = '/workspace/AI-music-score-featch'
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ['PYTHONPATH'] = ROOT

TASK_ID = 'test-001'

print("=== AI Guitar Tab 扒谱测试 ===\n")

for audio_file in [
    'test_audio/fb89949e-2e61-464b-bfac-22e7750db3fa.wav',
    'test_audio/test_guitar.wav',
]:
    full_path = f'{ROOT}/{audio_file}'
    if not os.path.exists(full_path):
        print(f"跳过不存在: {full_path}\n")
        continue

    data, sr = sf.read(full_path)
    dur = len(data) / sr
    print(f"▶ {audio_file}")
    print(f"  参数: {sr}Hz | {dur:.2f}秒 | {data.shape}")

    from backend.core.bpm_detector import detect_bpm
    from backend.core.chord_recognizer import recognize_chords, recognize_bass_notes
    from backend.core.basic_pitch_transcriber import is_available, transcribe
    from backend.core.score_generator import build_gta_text, build_midi_file

    # BPM
    r_bpm = detect_bpm(full_path, TASK_ID)
    bpm_val = r_bpm.get('bpm', 120) if isinstance(r_bpm, dict) else 120
    print(f"  BPM: {bpm_val} (raw: {r_bpm})")

    # 和弦
    chords = recognize_chords(full_path, TASK_ID)
    print(f"  和弦: {len(chords)} 个 → {chords[:5] if chords else '无'}")

    # Bass
    bass = recognize_bass_notes(full_path, TASK_ID)
    print(f"  Bass: {len(bass)} 个音符")
    for b in bass[:3]:
        print(f"    {b.get('start',0):.2f}s | {b.get('note','?')} | 弦{b.get('string','?')}/品{b.get('fret','?')} | conf {b.get('confidence',0):.2f}")

    # Guitar音符
    if is_available():
        notes = transcribe(full_path, TASK_ID)
        print(f"  Guitar音符: {len(notes)} 个")
    else:
        notes = []
        print(f"  Guitar音符: ⚠️ basic_pitch未装")

    # GTA文本谱（正确签名：chords, guitar_pitch, bpm_dict, bass_notes）
    print(f"  GTA文本谱生成中...")
    try:
        gta = build_gta_text(
            chords=chords,
            guitar_pitch={},       # Demo模式为空
            bpm={'bpm': bpm_val, 'time_signature': r_bpm.get('time_signature','4/4')},
            song_name=os.path.basename(audio_file),
            artist='AI-Test',
            bass_notes=bass
        )
        lines = gta.split('\n')
        print(f"  ✅ GTA谱: {len(lines)} 行")
        for l in lines[:12]:
            print(f"    | {l}")
    except Exception as e:
        print(f"  ❌ GTA错误: {e}")

    # MIDI（正确签名：chords, bass, bpm_int, output_path）
    out_dir = f'{ROOT}/backend/test_out'
    os.makedirs(out_dir, exist_ok=True)
    midi_name = f'{TASK_ID}_{os.path.basename(audio_file)}.mid'
    midi_path = f'{out_dir}/{midi_name}'
    try:
        midi_file = build_midi_file(chords, bass, bpm_val, midi_path)
        size = os.path.getsize(midi_file) if os.path.exists(midi_file) else 0
        print(f"  ✅ MIDI: {midi_file} ({size} bytes)")
    except Exception as e:
        print(f"  ❌ MIDI错误: {e}")

    print()

print("=== 测试完成 ===")
