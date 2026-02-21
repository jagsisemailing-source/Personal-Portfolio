import openai
import json

class MusicGenerator:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key="xxxxx")
    
    def generate_music_data(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a music composition assistant. Generate musical note data in JSON format for three separate tracks: instrument, bass, and drums. This should be tracks that can be looped to make one overarching beat, bassically a sample.
                The output should be a JSON object with:
                - "instrument": {
                    "notes": an array of objects, each containing:
                      * "pitch": MIDI note number (60 = middle C) OR "pitches": array of MIDI numbers for chords
                      * "duration": in beats
                      * "time": start time in beats
                      * "velocity": volume (0-127)
                    "program": MIDI instrument number (0-127)
                  }
                - "bass": {
                    "notes": an array of objects (same structure as instrument but only single pitches)
                    "program": MIDI bass instrument number (32-39 recommended)
                  }
                - "drums": {
                    "notes": an array of objects (using General MIDI drum note numbers)
                  }
                - "tempo": in BPM (must be between 60-180)
                - "time_signature": "4/4" or similar
                - "total_beats": total length of composition in beats (must be at least 20 beats)
                
                Calculations for time:
                 Total Beats = (BPM / 60) * 20

                    Example (120 BPM): (120 / 60) * 20 = 40 beats

                 Bars in 4/4 = Total Beats / 4

                    Example (120 BPM): 40 / 4 = 10 bars

                 Exact BPM for Whole Bars = (Desired Bars * Beats per Bar * 60) / 20

                    Example (8 bars in 4/4): (8 * 4 * 60) / 20 = 96 BPM

                 Samples (44.1kHz) = 44100 * 20 = 882,000 samples

                 Frames (NTSC 29.97fps) = 20 * 29.97 ≈ 600 frames

                 Common BPM/Bar Combos for 20sec:

                 120 BPM, 4/4 = 10 bars

                 96 BPM, 4/4 = 8 bars

                 135 BPM, 3/4 = 15 bars

                 Variable Tempo: Sum of all segment durations must = 20sec.
                
                 Notes:
                 Keep everything as integers, not floats

                Important Guidelines:
                1. First choose a tempo between 60-180 BPM
                2. Then set total_beats to at least tempo
                3. Instrument track should be melodic/harmonic (chords and melodies) and should be very original
                4. Bass track should complement but not duplicate the instrument track, have lots of pressure with pauses that compliment the instrument and drums
                5. Drums track should use General MIDI drum mapping (channel 10)
                6. All tracks must end at the same time (total_beats)
                7. Use music theory for harmonic relationships between tracks
                8. No direct repetition - create evolving musical ideas
                9. The drums should be very complex
                10. The Track itself should be original, no basic patterns, have lots of complexeity and almsot shifting music"""},
                    {"role": "user", "content": f"Create a three-part musical piece based on: {prompt}. Use tempo between 60-180 BPM and set total_beats to at least (tempo / 3) to ensure minimum 20 seconds duration."}
                ],
                response_format={"type": "json_object"}
            )
            
            music_data = json.loads(response.choices[0].message.content)
            
            # Calculate and verify duration
            tempo = music_data.get("tempo", 120)
            total_beats = music_data.get("total_beats", max(40, int(tempo / 3 * 2)))
            calculated_duration = (total_beats * 60) / tempo
            
            # Force minimum duration of 20 seconds
            if calculated_duration < 20:
                total_beats = int((20 * tempo) / 60)
                music_data["total_beats"] = total_beats
                calculated_duration = 20
            
            return {
                "status": "success",
                "music_data": music_data,
                "metadata": {
                    "tempo": tempo,
                    "time_signature": music_data.get("time_signature"),
                    "duration": calculated_duration,
                    "total_beats": total_beats,
                    "instrument_program": music_data["instrument"].get("program"),
                    "bass_program": music_data["bass"].get("program")
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == "__main__":
    # Example usage
    generator = MusicGenerator(api_key="your-api-key")
    prompt = input("Enter your music prompt: ")
    result = generator.generate_music_data(prompt)
    
    if result["status"] == "success":
        print("Successfully generated music data:")
        print(json.dumps(result["music_data"], indent=2))
    else:
        print(f"Error: {result['message']}")