import streamlit as st
import os
import zipfile
from datetime import datetime
import pygame
import tempfile
import numpy as np
from pretty_midi import PrettyMIDI, Instrument
import soundfile as sf
from music_generation_api import MusicGenerator
from midi_conversion_api import MIDIConverter

OUTPUT_FOLDER = "generated_music"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def create_timestamped_folder():
    """Create a unique folder for each generation session"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(OUTPUT_FOLDER, timestamp)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# Drum sample generator with fixed lengths
def generate_drum_samples():
    """Create properly sized drum samples"""
    sample_rate = 44100
    duration = 0.1  # 100ms for all samples
    samples = {
        'kick': np.zeros(int(duration * sample_rate)),
        'snare': np.zeros(int(duration * sample_rate)),
        'hihat': np.zeros(int(duration * sample_rate))
    }
    
    t = np.linspace(0, duration, len(samples['kick']))
    
    # Kick drum (low frequency pulse)
    samples['kick'] = 0.5 * np.sin(2 * np.pi * 50 * t) * np.exp(-10 * t)
    
    # Snare (noise burst)
    samples['snare'] = np.random.uniform(-1, 1, len(t)) * np.exp(-15 * t)
    
    # Hi-hat (high frequency burst)
    samples['hihat'] = 0.3 * np.sin(2 * np.pi * 8000 * t) * np.exp(-50 * t)
    
    return samples

DRUM_SAMPLES = generate_drum_samples()

def enhance_drum_track(midi_path):
    """Safer drum track enhancement"""
    try:
        midi = PrettyMIDI(midi_path)
        if not midi.instruments:
            return None
            
        # Create output audio buffer
        end_time = midi.get_end_time()
        audio = np.zeros(int(end_time * 44100) + 44100)
        sample_len = len(DRUM_SAMPLES['kick'])
        
        for note in midi.instruments[0].notes:
            start = int(note.start * 44100)
            end = start + sample_len
            
            # Select appropriate sample
            if note.pitch == 36:  # Kick
                sample = DRUM_SAMPLES['kick']
            elif note.pitch == 38 or note.pitch == 40:  # Snare
                sample = DRUM_SAMPLES['snare']
            else:  # Hi-hat/cymbal
                sample = DRUM_SAMPLES['hihat']
            
            # Safe mixing
            if end <= len(audio):
                audio[start:end] += sample[:end-start]
        
        return audio
    except Exception as e:
        st.error(f"Drum processing error: {str(e)}")
        return None

def generate_wav_preview(midi_path, is_drum=False):
    """More robust WAV generation"""
    try:
        if is_drum:
            audio = enhance_drum_track(midi_path)
        else:
            midi = PrettyMIDI(midi_path)
            audio = midi.synthesize(fs=44100)
        
        if audio is None or len(audio) == 0:
            return None
            
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = 0.7 * audio / max_val
        
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_wav.name, audio, 44100)
        temp_wav.close()
        return temp_wav.name
        
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
        return None

def main():
    st.title("🎵 AI Music Generator")
    st.markdown("Generate custom music with AI")

    # Initialize pygame with enough channels
    pygame.mixer.init(frequency=44100, size=-16, channels=6, buffer=4096)

    # Session state
    if 'generated' not in st.session_state:
        st.session_state.update({
            'generated': False,
            'midi_files': None,
            'wav_files': None,
            'temp_files': []
        })

    # Clear session
    if st.button("🧹 Clear Session"):
        pygame.mixer.stop()
        for file in st.session_state.temp_files:
            try:
                if os.path.exists(file):
                    os.unlink(file)
            except:
                pass
        st.session_state.update({
            'generated': False,
            'midi_files': None,
            'wav_files': None,
            'temp_files': []
        })
        st.rerun()

    # Music generation
    prompt = st.text_area("Describe your music:", height=100)
    
    if st.button("🎶 Generate Music") and prompt:
        with st.spinner("Creating your music..."):
            try:
                output_folder = create_timestamped_folder()
                os.makedirs(output_folder, exist_ok=True)
                
                # Generate MIDI files
                midi_files = {
                    'instrument': os.path.join(output_folder, 'instrument.mid'),
                    'bass': os.path.join(output_folder, 'bass.mid'),
                    'drums': os.path.join(output_folder, 'drums.mid')
                }
                
                generator = MusicGenerator(api_key="your-api-key")
                converter = MIDIConverter()
                
                gen_result = generator.generate_music_data(prompt)
                if gen_result.get("status") != "success":
                    st.error("Generation failed")
                    return
                
                midi_result = converter.convert_to_midi(
                    gen_result["music_data"],
                    instrument_file=midi_files["instrument"],
                    bass_file=midi_files["bass"],
                    drums_file=midi_files["drums"]
                )
                
                if midi_result.get("status") != "success":
                    st.error("MIDI conversion failed")
                    return
                
                wav_files = {
                    'instrument': generate_wav_preview(midi_files["instrument"]),
                    'bass': generate_wav_preview(midi_files["bass"]),
                    'drums': generate_wav_preview(midi_files["drums"], is_drum=True)
                }
                
                if not all(wav_files.values()):
                    st.error("Failed to create audio previews")
                    return
                
                # Update session state
                st.session_state.update({
                    'generated': True,
                    'midi_files': midi_files,
                    'wav_files': wav_files,
                    'temp_files': list(wav_files.values())
                })
                st.success("Music generated!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Preview and downloads
    if st.session_state.generated:
        # Playback controls
        st.subheader("Enhanced Preview")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Play All Tracks"):
                pygame.mixer.stop()
                for i, (name, wav_path) in enumerate(st.session_state.wav_files.items()):
                    try:
                        sound = pygame.mixer.Sound(wav_path)
                        pygame.mixer.Channel(i).play(sound)
                    except:
                        pass
                st.success("Playing enhanced mix!")
        with col2:
            if st.button("⏹️ Stop All"):
                pygame.mixer.stop()
                st.info("Playback stopped")

        # Individual track controls
        st.subheader("Track Controls")
        cols = st.columns(3)
        for i, (name, wav_path) in enumerate(st.session_state.wav_files.items()):
            with cols[i]:
                st.write(f"**{name.capitalize()} Track**")
                if st.button(f"▶️ Play {name}", key=f"play_{name}"):
                    sound = pygame.mixer.Sound(wav_path)
                    pygame.mixer.Channel(i).play(sound)
                if st.button(f"⏹️ Stop {name}", key=f"stop_{name}"):
                    pygame.mixer.Channel(i).stop()

        # Downloads
        st.subheader("Download")
        zip_path = os.path.join(os.path.dirname(st.session_state.midi_files["instrument"]), "tracks.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in st.session_state.midi_files.values():
                zipf.write(file, os.path.basename(file))
        
        with open(zip_path, "rb") as f:
            st.download_button(
                "Download All (ZIP)",
                f,
                file_name="music_tracks.zip"
            )

        cols = st.columns(3)
        for i, (name, path) in enumerate(st.session_state.midi_files.items()):
            with cols[i]:
                with open(path, "rb") as f:
                    st.download_button(
                        f"⬇️ {name.capitalize()} Track",
                        f,
                        file_name=f"{name}.mid"
                    )

if __name__ == "__main__":
    main()