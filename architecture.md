# TTS architecture
```mermaid
flowchart TD
subgraph ui["application layer"]
    gui["GUI Tkinter"]
    upload["upload text or markdown"]
    customvoice["select custom voice"]
    lang["select language"]
    convert["convert to audio"]
end

subgraph clonevoice["clone voice inputs"]
    aupload["upload reference audio"]
    txtfile["upload reference transcript"]
end

subgraph text["text processing layer"]
    load["load text"]
    strip["strip text"]
    chunk["text chunks"]
    load_ref_txt["load ref transcript"]
end

subgraph engine["inference engine"]
    ttsengine["Qwen3-TTS Model"]
end

out["output wav files"]

%% Step 1: User fills in all GUI inputs
gui --> upload
gui --> customvoice
gui --> aupload
gui --> txtfile
gui --> lang

%% Step 2: User clicks Convert — triggers the pipeline
gui --> convert

%% Step 3: Document text processing
convert --> load
upload -->|filepath| load
load -->|raw text| strip
strip -->|clean text| chunk

%% Step 4: Clone voice reference inputs processed in parallel
txtfile -->|transcript path| load_ref_txt
load_ref_txt -->|plain text| ttsengine
aupload -->|audio path| ttsengine

%% Step 5: All processed inputs converge at the engine
chunk -->|list of text chunks| ttsengine
customvoice -->|speaker name| ttsengine
lang -->|language string| ttsengine

%% Step 6: Engine generates and saves output
ttsengine -->|save wav| out
```

---

# Pre-development Architecture (Batch Synthesis Route)

> This pipeline was used before the desktop app was built. It is a standalone CLI script
> (`scripts/synthesize_manifest.py`) that batch-generates audio assets from a JSON manifest.

```mermaid
flowchart TD

subgraph inputs["inputs"]
    manifest[("manifest.json clip list")]
    ref_audio["refs/indian_female_calm.wav reference audio"]
    ref_text["hardcoded reference transcript text"]
end

subgraph batch["batch processing layer"]
    parse["parse clips from manifest"]
    tags["read clip tags"]
    tag_style["assign delivery style by tag priority"]
end

subgraph b_engine["inference engine"]
    b_model["Qwen3-TTS-12Hz-0.6B-Base voice cloning model"]
end

subgraph audio_post["audio post-processing"]
    mono["convert to mono"]
    resample["resample to 48000 Hz via soxr"]
    silence["insert gap silence between clips"]
    concat["concatenate all clips"]
end

subgraph outputs["outputs"]
    clips["output/clips - flac and mp3 segments"]
    combined["output/combined - full flac and mp3"]
    timestamps["output/combined/timestamps.json"]
end

%% Step 1: Read manifest
manifest -->|clip entries| parse

%% Step 2: Assign style per clip
parse -->|clip text and tags| tags
tags -->|matched tag| tag_style

%% Step 3: Load model once, synthesize each clip
tag_style -->|instruct string| b_model
ref_audio -->|reference audio path| b_model
ref_text -->|reference transcript| b_model

%% Step 4: Post-process each clip audio
b_model -->|raw audio array| mono
mono -->|mono audio| resample

%% Step 5: Write individual clips
resample -->|resampled clip| clips

%% Step 6: Build combined track
resample -->|resampled clip| silence
silence -->|padded clip| concat
concat -->|full audio array| combined
concat -->|offset timings| timestamps
```