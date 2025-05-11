import os
import wave
import struct
import pyaudio
from PyQt6.QtCore import QThread, pyqtSignal

class AudioRecorder(QThread):
    """Thread for recording audio without blocking the main GUI thread."""
    
    status_update = pyqtSignal(str)
    recording_level = pyqtSignal(float)
    finished = pyqtSignal(str)
    
    def __init__(self, selected_device_index, speaker_name, sentence_id):
        super().__init__()
        self.device_index = selected_device_index
        self.speaker_name = speaker_name
        self.sentence_id = sentence_id
        self.is_recording = False
        self.audio_data = []
        self.filename = f"{speaker_name}_{sentence_id}.wav"
        
        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        
    def run(self):
        """Start recording audio in a separate thread."""
        self.is_recording = True
        self.audio_data = []
        
        # Open stream
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk
        )
        
        self.status_update.emit("Recording...")
        
        # Record audio
        while self.is_recording:
            data = stream.read(self.chunk)
            self.audio_data.append(data)
            
            # Calculate and emit audio level for visualization
            audio_level = self._calculate_audio_level(data)
            self.recording_level.emit(audio_level)
        
        # Close stream
        stream.stop_stream()
        stream.close()
        
        if len(self.audio_data) > 0:
            self.status_update.emit("Processing recording...")
            self.finished.emit("Recording completed")
        else:
            self.status_update.emit("Recording cancelled")
            self.finished.emit("Recording cancelled")
    
    def save_audio(self, output_dir):
        """Save the recorded audio to a WAV file."""
        if not self.audio_data:
            return None
            
        wavs_dir = os.path.join(output_dir, "wavs")
        os.makedirs(wavs_dir, exist_ok=True)
        
        filename = os.path.join(wavs_dir, self.filename)
        
        # Save the audio data to a WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.audio_data))
        
        return filename
    
    def stop_recording(self):
        """Stop the audio recording."""
        self.is_recording = False
    
    def _calculate_audio_level(self, data):
        """Calculate audio level from chunk for visualization."""
        count = len(data) / 2
        format = "%dh" % count
        shorts = struct.unpack(format, data)
        
        # Get absolute values to find the maximum
        abs_values = [abs(s) for s in shorts]
        if abs_values:
            # Normalize to 0-1 range
            max_amplitude = max(abs_values)
            normalized = max_amplitude / 32768.0  # 16-bit audio normalization
            return normalized
        return 0.0