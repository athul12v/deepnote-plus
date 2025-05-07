import os
from flask import Flask, render_template, request, jsonify
import whisper
import soundfile as sf
import io
import numpy as np
from collections import Counter
from scipy.signal import butter, lfilter

app = Flask(__name__)

# Load the Whisper model (adjust the model size if needed: tiny, base, small, medium, large)
model = whisper.load_model("base")
sampling_rate = 16000  # Standard sampling rate for Whisper

def transcribe_audio(audio_bytes):
    """Transcribes audio bytes using OpenAI Whisper."""
    try:
        audio_np, sr = sf.read(io.BytesIO(audio_bytes), samplerate=None)
        if sr != sampling_rate:
            raise ValueError(f"Audio sample rate ({sr}) does not match expected rate ({sampling_rate})")
        transcription = model.transcribe(audio_np)['text']
        return transcription
    except Exception as e:
        return f"Error during transcription: {e}"

def find_most_stressed_word(transcription):
    """Finds the most frequent word in the transcription (approximation of stress)."""
    if not transcription:
        return None
    words = transcription.lower().split()
    word_counts = Counter(words)
    most_common = word_counts.most_common(1)
    return most_common[0][0] if most_common else None

# Basic audio cleaning function (simple low-pass filter - may not be very effective for all noise)
def apply_low_pass_filter(audio_data, cutoff_freq, sample_rate, order=4):
    """Applies a simple low-pass filter to the audio data."""
    nyquist_freq = 0.5 * sample_rate
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    filtered_audio = lfilter(b, a, audio_data)
    return filtered_audio

@app.route('/', methods=['GET'])
def index():
    return render_template('client.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file part'})
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({'error': 'No selected audio file'})
    if file:
        audio_bytes = file.read()
        transcription = transcribe_audio(audio_bytes)
        most_stressed = find_most_stressed_word(transcription)
        return jsonify({'transcription': transcription, 'most_stressed': most_stressed})

@app.route('/record', methods=['POST'])
def record_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio data received'})
    audio_file = request.files['audio_data']
    audio_bytes = audio_file.read()

    # Basic noise reduction (you might need more sophisticated techniques)
    try:
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32) # Assuming audio is sent as float32 array
        cleaned_audio = apply_low_pass_filter(audio_array, cutoff_freq=4000, sample_rate=sampling_rate)
        cleaned_audio_bytes = io.BytesIO()
        sf.write(cleaned_audio_bytes, cleaned_audio, samplerate=sampling_rate, format='WAV') # Use a format that sf can handle
        cleaned_audio_bytes.seek(0)
        transcription = transcribe_audio(cleaned_audio_bytes.read())
        most_stressed = find_most_stressed_word(transcription)
        return jsonify({'transcription': transcription, 'most_stressed': most_stressed})
    except Exception as e:
        return jsonify({'error': f'Error processing recorded audio: {e}'})

if __name__ == '__main__':
    app.run(debug=True)