import os
import csv
import random
import pyaudio
import time
from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QFileDialog, QComboBox, 
                            QMessageBox, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from audio.recorder import AudioRecorder
from utils.audio_utils import get_input_devices

class TTSDatasetCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Variables for TTS dataset creation
        self.input_file = None
        self.speaker_name = None
        self.output_dir = None
        self.sentences = []
        self.current_sentence_index = 0
        self.done_sentences = set()
        self.done_sentences_file = None
        self.metadata_file = None
        
        # Audio recorder
        self.recorder = None
        self.recording = False
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        # Timer for updating UI
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.update_ui)
        self.level_timer.start(100)  # update every 100ms
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("TTS Dataset Creator")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Setup section - Speaker name
        setup_layout = QHBoxLayout()
        setup_layout.addWidget(QLabel("Speaker Name:"))
        self.speaker_name_input = QLineEdit()
        setup_layout.addWidget(self.speaker_name_input)
        main_layout.addLayout(setup_layout)
        
        # File selection section
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Input CSV:"))
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        file_layout.addWidget(self.file_path_display)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_csv)
        file_layout.addWidget(self.browse_button)
        main_layout.addLayout(file_layout)
        
        # Microphone selection section
        mic_layout = QHBoxLayout()
        mic_layout.addWidget(QLabel("Microphone:"))
        self.mic_selector = QComboBox()
        self.populate_microphones()
        mic_layout.addWidget(self.mic_selector)
        main_layout.addLayout(mic_layout)
        
        # Start button
        self.start_button = QPushButton("Start Session")
        self.start_button.clicked.connect(self.start_session)
        main_layout.addWidget(self.start_button)
        
        # Recording section (initially hidden)
        self.recording_widget = QWidget()
        recording_layout = QVBoxLayout(self.recording_widget)
        
        # Sentence display
        self.sentence_id_label = QLabel("ID: ")
        recording_layout.addWidget(self.sentence_id_label)
        
        self.sentence_display = QTextEdit()
        self.sentence_display.setReadOnly(True)
        font = QFont()
        font.setPointSize(20)
        self.sentence_display.setFont(font)
        recording_layout.addWidget(self.sentence_display)

        # Audio level display
        self.level_label = QLabel("Audio Level:")
        recording_layout.addWidget(self.level_label)
        self.level_bar = QProgressBar()
        self.level_bar.setTextVisible(False)
        recording_layout.addWidget(self.level_bar)
        
        # Status display
        self.status_label = QLabel("Press SPACE to start recording")
        recording_layout.addWidget(self.status_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.record_button = QPushButton("Record (SPACE)")
        self.record_button.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_button)
        
        self.next_button = QPushButton("Save & Next (n)")
        self.next_button.clicked.connect(self.save_and_next)
        self.next_button.setEnabled(False)
        control_layout.addWidget(self.next_button)
        
        self.discard_button = QPushButton("Discard (d)")
        self.discard_button.clicked.connect(self.discard_recording)
        self.discard_button.setEnabled(False)
        control_layout.addWidget(self.discard_button)
        
        self.skip_button = QPushButton("Skip (s)")
        self.skip_button.clicked.connect(self.skip_sentence)
        control_layout.addWidget(self.skip_button)
        
        recording_layout.addLayout(control_layout)
        
        # Progress display
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("Progress: 0/0")
        progress_layout.addWidget(self.progress_label)
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        recording_layout.addLayout(progress_layout)
        
        # End session button
        self.end_button = QPushButton("End Session")
        self.end_button.clicked.connect(self.end_session)
        recording_layout.addWidget(self.end_button)
        
        # Hidden by default
        self.recording_widget.setVisible(False)
        main_layout.addWidget(self.recording_widget)
        
        # Help text
        help_text = """
        Controls:
        • SPACE: Start/Stop recording
        • N: Save the recording and move to the next sentence
        • D: Discard the recording and re-record
        • S: Skip the current sentence
        """
        help_label = QLabel(help_text)
        main_layout.addWidget(help_label)
        
        # Status bar
        self.statusBar().showMessage("Ready")

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for the application."""
        # Space for start/stop recording
        self.shortcut_space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.shortcut_space.activated.connect(self.toggle_recording)
        
        # N for next sentence
        self.shortcut_n = QShortcut(QKeySequence("N"), self)
        self.shortcut_n.activated.connect(self.save_and_next)
        
        # D for discard
        self.shortcut_d = QShortcut(QKeySequence("D"), self)
        self.shortcut_d.activated.connect(self.discard_recording)
        
        # S for skip
        self.shortcut_s = QShortcut(QKeySequence("S"), self)
        self.shortcut_s.activated.connect(self.skip_sentence)

    def populate_microphones(self):
        """Populate the microphone dropdown with available devices."""
        try:
            devices = get_input_devices()
            for idx, name in devices:
                self.mic_selector.addItem(f"{name} (Index: {idx})", idx)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to enumerate audio devices: {str(e)}")
    
    def browse_csv(self):
        """Open file dialog to select input CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input CSV File", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.input_file = file_path
            self.file_path_display.setText(file_path)
    
    def start_session(self):
        """Initialize the recording session."""
        # Validate inputs
        if not self.input_file:
            QMessageBox.warning(self, "Error", "Please select an input CSV file.")
            return
        
        self.speaker_name = self.speaker_name_input.text().strip()
        if not self.speaker_name:
            QMessageBox.warning(self, "Error", "Please enter a speaker name.")
            return
        
        # Create speaker directory
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(self.input_file)), self.speaker_name)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "wavs"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "txt"), exist_ok=True)
        
        # Load sentences from CSV
        try:
            self.load_sentences()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sentences: {str(e)}")
            return
        
        # Initialize done sentences tracking
        self.done_sentences_file = os.path.join(self.output_dir, f"{self.speaker_name}_DONE_SENTENCES.txt")
        self.load_done_sentences()
        
        # Initialize metadata file
        self.metadata_file = os.path.join(self.output_dir, "metadata.csv")
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='|')
                writer.writerow(["audio_file", "text"])
        
        # Update UI state
        self.recording_widget.setVisible(True)
        self.start_button.setEnabled(False)
        self.speaker_name_input.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.mic_selector.setEnabled(False)
        
        # Load first sentence
        if self.sentences:
            self.load_next_sentence()
            self.update_progress()
        else:
            QMessageBox.information(self, "Info", "No sentences to record.")
            self.end_session()
    
    def load_sentences(self):
        """Load sentences from the input CSV file."""
        sentences = []
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            # Verify expected columns
            if len(header) < 2 or 'unique_id' not in header or 'text_sentences' not in header:
                raise ValueError("CSV must contain 'unique_id' and 'text_sentences' columns")
            
            id_idx = header.index('unique_id')
            text_idx = header.index('text_sentences')
            
            for row in reader:
                if len(row) > max(id_idx, text_idx):
                    sentences.append({
                        'id': row[id_idx],
                        'text': row[text_idx]
                    })
        
        # Shuffle sentences for better voice diversity
        random.shuffle(sentences)
        
        self.sentences = sentences
        
        self.statusBar().showMessage(f"Loaded {len(sentences)} sentences.")
    
    def load_done_sentences(self):
        """Load list of already completed sentences."""
        self.done_sentences = set()
        if os.path.exists(self.done_sentences_file):
            with open(self.done_sentences_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.done_sentences.add(line.strip())
    
    def load_next_sentence(self):
        """Load the next unrecorded sentence."""
        # Find next unrecorded sentence
        sentences_remaining = False
        
        while self.current_sentence_index < len(self.sentences):
            current = self.sentences[self.current_sentence_index]
            if current['id'] not in self.done_sentences:
                sentences_remaining = True
                break
            self.current_sentence_index += 1
        
        if not sentences_remaining:
            QMessageBox.information(self, "Complete", "All sentences have been recorded!")
            self.end_session()
            return
        
        # Display the sentence
        current = self.sentences[self.current_sentence_index]
        self.sentence_id_label.setText(f"ID: {current['id']}")
        self.sentence_display.setText(current['text'])
        self.statusBar().showMessage(f"Sentence {self.current_sentence_index + 1} of {len(self.sentences)}")
    
    def toggle_recording(self):
        """Start or stop recording audio."""
        if self.recording:
            # Stop recording
            self.recorder.stop_recording()
            self.recording = False
            self.record_button.setText("Record (SPACE)")
            self.status_label.setText("Recording stopped. Press SPACE to re-record, N to save.")
            self.next_button.setEnabled(True)
            self.discard_button.setEnabled(True)
        else:
            # Start recording
            selected_device_index = self.mic_selector.currentData()
            current = self.sentences[self.current_sentence_index]
            
            self.recorder = AudioRecorder(selected_device_index, self.speaker_name, current['id'])
            self.recorder.status_update.connect(self.update_status)
            self.recorder.recording_level.connect(self.update_level)
            self.recorder.finished.connect(self.recording_finished)
            
            self.recorder.start()
            self.recording = True
            self.record_button.setText("Stop (SPACE)")
            self.next_button.setEnabled(False)
            self.discard_button.setEnabled(False)
    
    def update_status(self, status):
        """Update the status label."""
        self.status_label.setText(status)
    
    def update_level(self, level):
        """Update the audio level display."""
        level_percent = int(level * 100)
        self.level_bar.setValue(level_percent)
        
        # Change color based on level
        if level_percent > 90:
            self.level_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif level_percent > 70:
            self.level_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.level_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
    
    def recording_finished(self, message):
        """Handle when recording is finished."""
        self.statusBar().showMessage(message)
    
    def save_and_next(self):
        """Save the current recording and move to the next sentence."""
        if not self.recorder or self.recording:
            return
        
        try:
            # Get current sentence
            current = self.sentences[self.current_sentence_index]
            
            # Save audio file
            audio_file = self.recorder.save_audio(self.output_dir)
            if not audio_file:
                self.status_label.setText("No recording to save. Please record first.")
                return
            
            audio_filename = os.path.basename(audio_file)
            
            # Save text file
            txt_dir = os.path.join(self.output_dir, "txt")
            txt_filename = f"{self.speaker_name}_{current['id']}.txt"
            with open(os.path.join(txt_dir, txt_filename), 'w', encoding='utf-8') as f:
                f.write(current['text'])
            
            # Update metadata
            with open(self.metadata_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='|')
                writer.writerow([audio_filename, current['text']])
            
            # Mark as done
            with open(self.done_sentences_file, 'a', encoding='utf-8') as f:
                f.write(f"{current['id']}\n")
            
            self.done_sentences.add(current['id'])
            
            # Move to next sentence
            self.current_sentence_index += 1
            self.load_next_sentence()
            self.update_progress()
            
            # Reset recording state
            self.next_button.setEnabled(False)
            self.discard_button.setEnabled(False)
            self.recorder = None
            
            self.status_label.setText("Saved successfully. Press SPACE to record next sentence.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save recording: {str(e)}")
    
    def discard_recording(self):
        """Discard the current recording and prepare to re-record."""
        if not self.recorder or self.recording:
            return
        
        self.recorder = None
        self.next_button.setEnabled(False)
        self.discard_button.setEnabled(False)
        self.status_label.setText("Recording discarded. Press SPACE to record.")
    
    def skip_sentence(self):
        """Skip the current sentence and move to the next one."""
        self.current_sentence_index += 1
        self.load_next_sentence()
        self.update_progress()
        
        # Reset recording state
        if self.recorder and not self.recording:
            self.recorder = None
        
        self.next_button.setEnabled(False)
        self.discard_button.setEnabled(False)
        self.status_label.setText("Sentence skipped. Press SPACE to record new sentence.")
    
    def update_progress(self):
        """Update the progress display."""
        total = len(self.sentences)
        done = len(self.done_sentences)
        percent = int((done / total) * 100) if total > 0 else 0
        
        self.progress_label.setText(f"Progress: {done}/{total}")
        self.progress_bar.setValue(percent)
    
    def update_ui(self):
        """Update UI elements periodically."""
        # This is called by the timer to keep UI responsive
        pass
    
    def end_session(self):
        """End the current recording session."""
        if self.recording:
            self.recorder.stop_recording()
        
        reply = QMessageBox.question(
            self, "End Session", 
            "Are you sure you want to end the session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset state
            self.recording_widget.setVisible(False)
            self.start_button.setEnabled(True)
            self.speaker_name_input.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.mic_selector.setEnabled(True)
            
            self.recorder = None
            self.recording = False
            self.sentences = []
            self.current_sentence_index = 0
            self.done_sentences = set()
            
            self.statusBar().showMessage("Session ended")