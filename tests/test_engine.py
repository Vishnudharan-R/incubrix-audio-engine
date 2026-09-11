import os
import pytest
from src.engine import AudioEngine
from src.schemas import AudioGenerationInput, VoiceControlParams, ConsentStatus

@pytest.fixture
def temp_engine(tmp_path):
    output_dir = tmp_path / "test_outputs"
    return AudioEngine(output_dir=str(output_dir))

def test_baseline_generation(temp_engine):
    payload = AudioGenerationInput(
        id="test_01",
        text="Dr. Smith ordered 50 percent more samples.",
        voice_id="default",
        controls=VoiceControlParams(rate=1.0, pitch=1.0)
    )
    
    manifest = temp_engine.generate_speech(payload)
    
    assert os.path.exists(manifest.output_wav_path)
    assert manifest.output_wav_path.endswith(".wav")
    assert manifest.audio_duration_seconds > 0.0
    assert manifest.consent_status == ConsentStatus.NOT_REQUIRED

def test_empty_input_validation(temp_engine):
    payload = AudioGenerationInput(
        id="test_empty",
        text="   ",
        voice_id="default"
    )
    
    with pytest.raises(ValueError, match="Input text cannot be empty"):
        temp_engine.generate_speech(payload)

def test_voice_adaptation_missing_consent(temp_engine):
    payload = AudioGenerationInput(
        id="test_clone_no_consent",
        text="Testing unconsented voice adaptation.",
        voice_id="cloned_voice",
        reference_audio_path="samples/ref.wav",
        consent_id=None
    )
    
    with pytest.raises(PermissionError, match="Voice adaptation blocked due to missing consent"):
        temp_engine.generate_speech(payload)

def test_voice_adaptation_approved_consent(temp_engine):
    payload = AudioGenerationInput(
        id="test_clone_with_consent",
        text="Testing consented voice adaptation.",
        voice_id="cloned_voice",
        reference_audio_path="samples/ref.wav",
        consent_id="CONSENT_RECORD_2026_001"
    )
    
    manifest = temp_engine.generate_speech(payload)
    assert manifest.consent_status == ConsentStatus.APPROVED