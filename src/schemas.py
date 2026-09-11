from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ConsentStatus(str, Enum):
    APPROVED = "APPROVED"
    MISSING = "MISSING"
    NOT_REQUIRED = "NOT_REQUIRED"

class VoiceControlParams(BaseModel):
    rate: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: float = Field(default=1.0, ge=0.0, le=2.0)

class AudioGenerationInput(BaseModel):
    id: str
    text: str
    voice_id: str = "voice_a"
    controls: VoiceControlParams = Field(default_factory=VoiceControlParams)
    reference_audio_path: Optional[str] = None
    consent_id: Optional[str] = None

class RunManifest(BaseModel):
    input_id: str
    model_name: str
    checkpoint_revision: str
    output_wav_path: str
    runtime_seconds: float
    peak_ram_mb: float
    warnings: List[str] = Field(default_factory=list)
    consent_status: ConsentStatus
    audio_duration_seconds: float
    real_time_factor: float