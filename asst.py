import speech_recognition as sr
from flask import Flask, request
import openai
import subprocess

app = Flask(__name__)

# Replace "your_api_key_here" with your actual OpenAI API key
openai.api_key = 'your_api_key_here'

recognizer = sr.Recognizer()

def listen_for_speech():
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    # Recognize speech using Google Speech Recognition
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def generate_response(prompt):
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      temperature=0.5,
      max_tokens=100,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    return response.choices[0].text.strip()

def text_to_speech(text):
    subprocess.run(['espeak', text])

@app.route('/voice-command')
def voice_command():
    spoken_command = listen_for_speech()
    print(f"Recognized: {spoken_command}")
    response_text = generate_response(spoken_command)
    text_to_speech(response_text)
    return response_text

@app.route('/text-command', methods=['GET'])
def text_command():
    text_command = request.args.get('command')
    if not text_command:
        return "No command provided", 400
    print(f"Command received: {text_command}")
    response_text = generate_response(text_command)
    text_to_speech(response_text)
    return response_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
