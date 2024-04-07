import sys
import speech_recognition as sr
from flask import Flask, request
import openai
import subprocess

# Initialize Flask only if not in CLI mode
if "--cli" not in sys.argv:
    app = Flask(__name__)

# Your OpenAI API key
openai.api_key = 'your_api_key_here'

recognizer = sr.Recognizer()

def listen_for_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
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

def handle_command(command):
    print(f"Command received: {command}")
    response_text = generate_response(command)
    text_to_speech(response_text)
    print(response_text)

# Web route for voice command
if "--cli" not in sys.argv:
    @app.route('/voice-command')
    def voice_command():
        spoken_command = listen_for_speech()
        print(f"Recognized: {spoken_command}")
        response_text = generate_response(spoken_command)
        text_to_speech(response_text)
        return response_text

    # Web route for text command
    @app.route('/text-command', methods=['GET'])
    def text_command():
        text_command = request.args.get('command')
        if not text_command:
            return "No command provided", 400
        handle_command(text_command)
        return response_text

# Main entry point
if __name__ == '__main__':
    if "--cli" in sys.argv:
        print("Entering CLI mode. Type 'exit' to quit.")
        while True:
            user_input = input("Enter your command: ")
            if user_input.lower() == 'exit':
                break
            handle_command(user_input)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
