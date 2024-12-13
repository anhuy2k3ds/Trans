import torch
import soundfile as sf
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from googletrans import Translator
import torchaudio
from gtts import gTTS
import pygame
import io

translator = Translator()

# Dịch văn bản
def translate_text(text, src_lang='en', dest_lang='vi'):
    try:
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        return f"Error: {str(e)}"

# Chuyển văn bản thành giọng nói và phát âm thanh trực tiếp
def text_to_speech(text, lang='vi'):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        pygame.mixer.init()
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error: {str(e)}")