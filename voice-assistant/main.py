from assistant import VoiceAssistant
from dataset import VoiceDatasetCollector
from diagnostics import AudioDiagnostics


def main() -> None:
    print("Choose a mode:")
    print("1. Run voice assistant")
    print("2. Collect voice dataset")
    print("3. Run audio diagnostics")
    choice = input("Enter 1, 2, or 3: ").strip()

    if choice == "2":
        collector = VoiceDatasetCollector()
        label = input("Enter a label for this sample group (for example: hello): ").strip() or "sample"
        count = int(input("How many samples? ").strip() or "5")
        for i in range(count):
            collector.record_sample(label, duration=3)
        print("Dataset collection complete.")
        return

    if choice == "3":
        AudioDiagnostics().run()
        return

    assistant = VoiceAssistant(name="Astra")
    print("Voice assistant initialized.")
    print("Microphone unavailable? You can still type your commands.")
    assistant.run()


if __name__ == "__main__":
    main()
