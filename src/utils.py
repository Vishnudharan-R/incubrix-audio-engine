import re
import psutil
import soundfile as sf

def normalize_text(raw_text: str) -> str:
    if not raw_text or not raw_text.strip():
        raise ValueError("Input text cannot be empty or whitespace.")
    
    text = raw_text.strip()
    text = re.sub(r'\bDr\b\.?', 'Doctor', text)
    text = re.sub(r'\bMr\b\.?', 'Mister', text)
    text = re.sub(r'\bMrs\b\.?', 'Missus', text)
    text = re.sub(r'\%', ' percent', text)
    text = re.sub(r'\&', ' and ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def get_audio_duration(file_path: str) -> float:
    info = sf.info(file_path)
    return float(info.duration)

class MemoryTracker:
    def __enter__(self):
        self.process = psutil.Process()
        self.start_mem = self.process.memory_info().rss / (1024 * 1024)
        self.peak_mem = self.start_mem
        return self

    def update(self):
        current_mem = self.process.memory_info().rss / (1024 * 1024)
        if current_mem > self.peak_mem:
            self.peak_mem = current_mem

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.update()