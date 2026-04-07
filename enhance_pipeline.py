#!/usr/bin/env python3
with open('/workspace/AI-music-score-featch/backend/core/pipeline.py', 'r') as f:
    content = f.read()

chunking_code = '''
# ─── 长音频分段处理 ──────────────────────────────────────────────
MAX_CHUNK_SEC = 90
CHUNK_OVERLAP = 5.0

def _chunk_audio(audio_path, output_dir, task_id):
    import librosa
    import soundfile as sf
    duration = librosa.get_duration(path=str(audio_path))
    if duration <= MAX_CHUNK_SEC:
        return [audio_path]
    chunk_paths = []
    start = 0.0
    chunk_idx = 0
    while start < duration:
        end = min(start + MAX_CHUNK_SEC, duration)
        chunk_path = output_dir / f"chunk_{chunk_idx:03d}.wav"
        y, sr = librosa.load(str(audio_path), sr=44100, offset=start, duration=end - start)
        sf.write(str(chunk_path), y, sr)
        chunk_paths.append(chunk_path)
        start = end - CHUNK_OVERLAP
        chunk_idx += 1
    logger.info(f"[{task_id}] Audio chunked: {len(chunk_paths)} segments")
    return chunk_paths

def _merge_chords(chunks_results, offset_step=None):
    if not chunks_results: return []
    if len(chunks_results) == 1: return chunks_results[0]
    merged = []
    offset = 0.0
    step = MAX_CHUNK_SEC - CHUNK_OVERLAP
    for chunk in chunks_results:
        for item in chunk:
            merged.append({"start": item["start"]+offset, "end": item["end"]+offset, "chord": item["chord"], "confidence": item.get("confidence", 1.0)})
        if chunk: offset += step
    return merged

def _merge_bass(bass_chunks):
    if not bass_chunks: return []
    if len(bass_chunks) == 1: return bass_chunks[0]
    merged = []
    offset = 0.0
    step = MAX_CHUNK_SEC - CHUNK_OVERLAP
    for chunk in bass_chunks:
        for note in chunk:
            merged.append({**{k: v for k, v in note.items() if k not in ("start","end")}, "start": note["start"]+offset, "end": note["end"]+offset})
        if chunk: offset += step
    return merged

'''

demo_marker = '# ─── 主 Pipeline ──────────────────────────────────────────────'
content = content.replace(demo_marker, chunking_code + demo_marker)

with open('/workspace/AI-music-score-featch/backend/core/pipeline.py', 'w') as f:
    f.write(content)

print("OK", "MAX_CHUNK_SEC" in content, "_chunk_audio" in content)
