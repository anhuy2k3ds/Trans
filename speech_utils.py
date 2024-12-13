import numpy as np
import speech_recognition as spr
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch

# Tải mô hình Wav2Vec2 và processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

# Biến cờ để dừng ghi âm
stop_recording_flag = False

# Nhận diện giọng nói từ dữ liệu âm thanh
def recognize_speech_from_audio(audio_data, sample_rate):
    # Chuyển đổi tần số lấy mẫu thành 16000 Hz nếu cần
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        audio_data = resampler(torch.tensor(audio_data)).numpy()
        sample_rate = 16000

    input_values = processor(audio_data, return_tensors="pt", padding="longest", sampling_rate=sample_rate).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids, clean_up_tokenization_spaces=True)[0]
    return transcription.lower()

# Nhận diện giọng nói từ micro
def recognize_speech_from_microphone():
    global stop_recording_flag
    recog = spr.Recognizer()
    try:
        with spr.Microphone() as source:
            print("Bắt đầu nói...")
            recog.adjust_for_ambient_noise(source, duration=0.2)
            while not stop_recording_flag:
                audio = recog.listen(source, timeout=3, phrase_time_limit=5)
                audio_data = np.frombuffer(audio.get_raw_data(), np.int16).astype(np.float32) / 32768.0
                sample_rate = audio.sample_rate
                return recognize_speech_from_audio(audio_data, sample_rate)
    except spr.UnknownValueError:
        return "Error: Google Speech Recognition could not understand the audio."
    except spr.RequestError as e:
        return f"Error: Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return f"Error: {str(e)}"

# Dừng phát âm thanh và ghi âm
def stop_speech():
    global stop_recording_flag
    stop_recording_flag = True