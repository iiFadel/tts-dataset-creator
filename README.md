# TTS Dataset Creator & Recorder

A GUI application for creating Text-to-Speech (TTS) datasets with a clean interface. This tool makes collecting voice samples organized and efficient for training TTS models.

## Features

- **Cross-platform**
  - Works on Windows, Linux, and macOS (Intel and Apple Silicon)
- **Clean GUI**
  - No command-line knowledge required
- **Metadata generation**
  -  Automatically generates metadata files required for TTS training
- **User-friendly Controls**
  - Keyboard shortcuts for fast workflow
- **Session Management**
  - Tracks progress and allows resuming sessions
- **Progress tracking**
  - Keep track of recorded sentences


## Requirements

- Python 3.8 or higher
- PyQt6
- PyAudio
- CSV input file with `unique_id` and `text_sentences` columns

## Project Structure

```
tts-dataset-creator/
├── main.py                   # Application entry point
├── requirements.txt          
├── README.md                 
├── src/
│   ├── __init__.py           
│   ├── audio_recorder.py     # AudioRecorder class
│   ├── gui/
│   │   ├── __init__.py       
│   │   ├── main_window.py    # TTSDatasetCreator main window
│   │   └── ui_components.py  # Additional UI components
│   └── utils/
│       ├── __init__.py       
│       └── file_utils.py     # File handling utilities
└── data/                     # Directory for sample data
    └── sample_sentences.csv  # Sentences input file
```

## Installation

1. Clone this repository:

```bash
git clone https://github.com/iiFadel/tts-dataset-creator.git
cd tts-dataset-creator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Note**: Installing PyAudio may require additional steps depending on your platform:

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Windows**:
You might need to install a pre-built wheel:
```bash
pip install pipwin
pipwin install pyaudio
```

## Usage

1. Start the application:

```bash
python main.py
```
or
```bash
python3 main.py
```

2. Configure your session:
   - Enter a Speaker Name (this will be used for folder creation)
   - Select your input CSV file (with `unique_id` and `text_sentences` columns)
   - Choose your microphone from the dropdown

3. Click Start Session

4. Use keyboard shortcuts for efficiency:
   - **SPACE**: Start/stop recording
   - **N**: Save current recording and move to next sentence
   - **D**: Discard current recording
   - **S**: Skip current sentence

The application will automatically create a structured dataset:

```
SPEAKERNAME/
├── wavs/
│   ├── SPEAKERNAME_SENTENCEID1.wav
│   ├── SPEAKERNAME_SENTENCEID2.wav
│   └── ...
├── txt/
│   ├── SPEAKERNAME_SENTENCEID1.txt
│   ├── SPEAKERNAME_SENTENCEID2.txt
│   └── ...
├── metadata.csv
└── SPEAKERNAME_DONE_SENTENCES.txt
```

## CSV Input Format

Your input CSV should contain at least these two columns:
- `unique_id`: A unique identifier for each sentence
- `text_sentences`: The text to be recorded

Example:
```csv
unique_id,text_sentences
001,"The birch canoe slid on the smooth planks."
002,"Glue the sheet to the dark blue background."
...
```

## Output Format

The application generates:

- **WAV files**
  - Named as `SPEAKERNAME_SENTENCEID.wav`
- **Text files**
  - Containing the raw sentence text
- **metadata.csv**
  - In the format `audio_file|text` for easy use with TTS systems
- **Done sentences log**
  - `SPEAKERNAME_DONE_SENTENCES.txt` 
  - Tracks completed recordings

## Citation / Attribution

If you use this tool in your research, project, or dataset collection process, please consider citing or referencing the author:

**Created by [Fadel Al Abbas](https://github.com/iiFadel)**  
- GitHub: [iiFadel](https://github.com/iiFadel)

## License
This codebase is released under the MIT License.  
Please refer to the [LICENSE](https://github.com/iiFadel/tts-dataset-creator/blob/main/LICENSE) file for more details.
