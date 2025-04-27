import warnings
import os
import logging
from vikusya.core import Vikusya

# Подавляем предупреждения от speechbrain, transformers и др.
warnings.filterwarnings("ignore", message="Module 'speechbrain.pretrained' was deprecated")
warnings.filterwarnings("ignore", message="Passing `gradient_checkpointing` to a config initialization is deprecated")
warnings.filterwarnings("ignore", message="Wav2Vec2Model is frozen.")

print("[Викуся]: Всё чистенько, без лишних предупреждений 💖")

if __name__ == "__main__":
    assistant = Vikusya()
    assistant.run()