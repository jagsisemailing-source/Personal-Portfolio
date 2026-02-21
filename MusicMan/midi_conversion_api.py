from midiutil import MIDIFile
import json

class MIDIConverter:
    def convert_to_midi(self, music_data, instrument_file="instrument.mid", 
                       bass_file="bass.mid", drums_file="drums.mid"):
        """Convert music data dictionary to MIDI files"""
        try:
            tempo = music_data.get("tempo", 120)
            
            # Instrument track
            midi_instrument = MIDIFile(1)
            midi_instrument.addTempo(track=0, time=0, tempo=tempo)
            midi_instrument.addProgramChange(
                tracknum=0, channel=0, time=0, 
                program=int(music_data["instrument"].get("program", 0))
            )
            
            for note in music_data["instrument"]["notes"]:
                if "pitch" in note:
                    midi_instrument.addNote(
                        track=0, channel=0,
                        pitch=note["pitch"],
                        time=note["time"],
                        duration=note["duration"],
                        volume=note.get("velocity", 100)
                    )
                elif "pitches" in note:
                    for pitch in note["pitches"]:
                        midi_instrument.addNote(
                            track=0, channel=0,
                            pitch=pitch,
                            time=note["time"],
                            duration=note["duration"],
                            volume=note.get("velocity", 100)
                        )
            
            # Bass track
            midi_bass = MIDIFile(1)
            midi_bass.addTempo(track=0, time=0, tempo=tempo)
            midi_bass.addProgramChange(
                tracknum=0, channel=1, time=0, 
                program=int(music_data["bass"].get("program", 32))
            )
            
            for note in music_data["bass"]["notes"]:
                midi_bass.addNote(
                    track=0, channel=1,
                    pitch=note["pitch"],
                    time=note["time"],
                    duration=note["duration"],
                    volume=note.get("velocity", 100)
                )
            
            # Drums track
            midi_drums = MIDIFile(1)
            midi_drums.addTempo(track=0, time=0, tempo=tempo)
            
            for note in music_data["drums"]["notes"]:
                midi_drums.addNote(
                    track=0, channel=9,
                    pitch=note["pitch"],
                    time=note["time"],
                    duration=note["duration"],
                    volume=note.get("velocity", 100)
                )
            
            # Write files
            with open(instrument_file, "wb") as f:
                midi_instrument.writeFile(f)
            with open(bass_file, "wb") as f:
                midi_bass.writeFile(f)
            with open(drums_file, "wb") as f:
                midi_drums.writeFile(f)
                
            return {
                "status": "success",
                "output_files": {
                    "instrument": instrument_file,
                    "bass": bass_file,
                    "drums": drums_file
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == "__main__":
    # Example usage
    converter = MIDIConverter()
    
    # Load music data from file or input
    music_json = input("Enter path to music data JSON file: ")
    with open(music_json) as f:
        music_data = json.load(f)
    
    result = converter.convert_to_midi(music_data)
    
    if result["status"] == "success":
        print("Successfully created MIDI files:")
        print(f"- Instrument: {result['output_files']['instrument']}")
        print(f"- Bass: {result['output_files']['bass']}")
        print(f"- Drums: {result['output_files']['drums']}")
    else:
        print(f"Error: {result['message']}")