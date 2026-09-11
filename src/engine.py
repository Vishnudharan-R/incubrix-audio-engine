import os
import time
import pyttsx3
from src.schemas import AudioGenerationInput, RunManifest, ConsentStatus
from src.utils import normalize_text, get_audio_duration, MemoryTracker

class AudioEngine:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.model_name = "pyttsx3-tts-engine"
        self.checkpoint_revision = "v2.90"

    def generate_speech(self, payload: AudioGenerationInput) -> RunManifest:
        warnings = []

        if payload.reference_audio_path:
            if not payload.consent_id or payload.consent_id.strip() == "":
                manifest = RunManifest(
                    input_id=payload.id,
                    model_name=self.model_name,
                    checkpoint_revision=self.checkpoint_revision,
                    output_wav_path="",
                    runtime_seconds=0.0,
                    peak_ram_mb=0.0,
                    warnings=["Blocked execution: Reference audio provided without valid consent ID."],
                    consent_status=ConsentStatus.MISSING,
                    audio_duration_seconds=0.0,
                    real_time_factor=0.0
                )
                self._save_manifest(payload.id, manifest)
                raise PermissionError("Voice adaptation blocked due to missing consent.")
            consent_state = ConsentStatus.APPROVED
        else:
            consent_state = ConsentStatus.NOT_REQUIRED

        clean_text = normalize_text(payload.text)
        wav_filename = f"{payload.id}.wav"
        output_wav_path = os.path.join(self.output_dir, wav_filename)

        start_time = time.time()

        with MemoryTracker() as mem_tracker:
            tts_engine = pyttsx3.init()
            
            # Select speaker voice based on voice_id
            voices = tts_engine.getProperty('voices')
            if payload.voice_id == "voice_b" and len(voices) > 1:
                tts_engine.setProperty('voice', voices[1].id)
            elif len(voices) > 0:
                tts_engine.setProperty('voice', voices[0].id)
                
            # Apply rate (speed) control
            default_rate = tts_engine.getProperty('rate')
            tts_engine.setProperty('rate', int(default_rate * payload.controls.rate))

            # Apply volume control
            tts_engine.setProperty('volume', payload.controls.volume)

            # Generate speech and output directly to WAV file
            tts_engine.save_to_file(clean_text, output_wav_path)
            tts_engine.runAndWait()
            mem_tracker.update()

        elapsed = time.time() - start_time
        audio_len = get_audio_duration(output_wav_path)
        rtf = elapsed / audio_len if audio_len > 0 else 0.0

        manifest = RunManifest(
            input_id=payload.id,
            model_name=self.model_name,
            checkpoint_revision=self.checkpoint_revision,
            output_wav_path=output_wav_path,
            runtime_seconds=round(elapsed, 4),
            peak_ram_mb=round(mem_tracker.peak_mem, 2),
            warnings=warnings,
            consent_status=consent_state,
            audio_duration_seconds=round(audio_len, 2),
            real_time_factor=round(rtf, 4)
        )

        self._save_manifest(payload.id, manifest)
        return manifest

    def _save_manifest(self, input_id: str, manifest: RunManifest):
        manifest_path = os.path.join(self.output_dir, f"{input_id}_manifest.json")
        with open(manifest_path, "w") as f:
            f.write(manifest.model_dump_json(indent=2))