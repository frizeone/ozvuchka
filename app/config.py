import os
from dataclasses import dataclass


@dataclass
class Config:
    input_dir: str = os.getenv('INPUT_DIR', '/input')
    output_dir: str = os.getenv('OUTPUT_DIR', '/output')
    language: str = os.getenv('LANGUAGE', 'ru')
    reference_audio: str = os.getenv('REFERENCE_AUDIO', '')
    output_format: str = os.getenv('OUTPUT_FORMAT', 'wav')
    sample_rate: int = int(os.getenv('SAMPLE_RATE', '24000'))
