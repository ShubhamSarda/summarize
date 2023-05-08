import openai
import moviepy.editor as mp
import speech_recognition as sr
from dotenv import load_dotenv
import os

# Load API key from environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API
openai.api_key = api_key

# Transcribe video
def transcribe_video(video_path: str) -> str:
    clip = mp.VideoFileClip(video_path)
    clip_audio = clip.audio
    clip_audio.write_audiofile("temp_audio.wav")
    r = sr.Recognizer()

    transcript = ""
    with sr.AudioFile("temp_audio.wav") as source:
        audio_length = int(clip_audio.duration)  # Calculate the total length of the audio
        processed_duration = 0
        while processed_duration < audio_length:
            try:
                audio_data = r.record(source, duration=30)  # Process 30 seconds at a time
                text = r.recognize_google(audio_data)
                transcript += text + " "
                processed_duration += 30                
            except sr.UnknownValueError:
                print("Could not understand audio")
                processed_duration += 30
            except sr.RequestError as e:
                if e.args[0] == "recognition request failed: Bad Request":
                    break
                else:
                    print(f"RequestError: {e.args[0]}")
                    processed_duration += 30
    
    print("Transcription Created")
    return transcript


# Summarize the transcription
def generate_summary(text, model="text-davinci-003"):
    prompt = f"Please provide a brief summary of the following text:\n\n{text}"
    response = openai.Completion.create(engine=model, prompt=prompt, max_tokens=500, n=1, stop=None, temperature=0.5)
    summary = response.choices[0].text.strip()
    print("Summary Completed")
    return summary

# Main function
def main(video_path, output_file):
    transcription = transcribe_video(video_path)
    summary = generate_summary(transcription)

    with open(output_file, "w") as f:
        f.write(summary)

if __name__ == "__main__":
    video_path = "input-version.mp4"
    output_file = "summary.txt"
    main(video_path, output_file)
