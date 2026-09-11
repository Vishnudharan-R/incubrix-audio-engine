import argparse
import json
import os
import sys
from src.engine import AudioEngine
from src.schemas import AudioGenerationInput, VoiceControlParams

def main():
    parser = argparse.ArgumentParser(description="IncuBrix Track 01 Baseline Speech Engine")
    parser.add_argument("--text", type=str, help="Single text sentence to synthesize")
    parser.add_argument("--id", type=str, default="baseline_01", help="Unique identifier string")
    parser.add_argument("--voice", type=str, default="voice_a", help="Voice choice: 'voice_a' or 'voice_b'")
    parser.add_argument("--batch", type=str, help="Path to batch JSON input file")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory where files are written")
    parser.add_argument("--rate", type=float, default=1.0, help="Speech rate multiplier")
    parser.add_argument("--pitch", type=float, default=1.0, help="Pitch shift multiplier")
    parser.add_argument("--volume", type=float, default=1.0, help="Volume energy multiplier")

    args = parser.parse_args()
    engine = AudioEngine(output_dir=args.output_dir)

    if args.batch:
        if not os.path.exists(args.batch):
            print(f"Error: Batch file '{args.batch}' not found.")
            sys.exit(1)

        with open(args.batch, "r") as f:
            items = json.load(f)

        print(f"Processing batch of {len(items)} inputs...")
        for item in items:
            item_id = item.get("id")
            manifest_path = os.path.join(args.output_dir, f"{item_id}_manifest.json")

            if os.path.exists(manifest_path):
                print(f"Skipping cached item '{item_id}' (manifest exists).")
                continue

            ctrl_data = item.get("controls", {})
            controls = VoiceControlParams(
                rate=ctrl_data.get("rate", 1.0),
                pitch=ctrl_data.get("pitch", 1.0),
                volume=ctrl_data.get("volume", 1.0)
            )

            payload = AudioGenerationInput(
                id=item_id,
                text=item.get("text", ""),
                voice_id=item.get("voice_id", "voice_a"),
                controls=controls,
                reference_audio_path=item.get("reference_audio_path"),
                consent_id=item.get("consent_id")
            )

            try:
                manifest = engine.generate_speech(payload)
                print(f"Success [{item_id}]: {manifest.output_wav_path}")
            except Exception as e:
                print(f"Failed [{item_id}]: {str(e)}")

    elif args.text:
        controls = VoiceControlParams(rate=args.rate, pitch=args.pitch, volume=args.volume)
        payload = AudioGenerationInput(
            id=args.id,
            text=args.text,
            voice_id=args.voice,
            controls=controls
        )

        try:
            manifest = engine.generate_speech(payload)
            print(f"Success: Saved to {manifest.output_wav_path}")
            print(f"Manifest: {os.path.join(args.output_dir, f'{args.id}_manifest.json')}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()