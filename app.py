from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import threading

app = Flask(__name__)
recognizer = sr.Recognizer()
mic = sr.Microphone()
recording = False
recognized_text = ""

def record_and_transcribe():
    global recognized_text, recording
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while recording:
            try:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                recognized_text += text + "\n"
                print("Recognized:", text)
            except sr.UnknownValueError:
                print("Could not understand the audio")
            except sr.RequestError:
                print("Speech recognition service unavailable")
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Speech Recognition API is running"}), 200

@app.route("/start", methods=["POST"])
def start_recording():
    global recording
    if not recording:
        recording = True
        threading.Thread(target=record_and_transcribe).start()
        return jsonify({"status": "success", "message": "Recording started"})
    return jsonify({"status": "error", "message": "Already recording"})

@app.route("/stop", methods=["POST"])
def stop_recording():
    global recording, recognized_text
    recording = False
    response = {"status": "success", "message": "Recording stopped", "data": {"text": recognized_text.strip()}}
    recognized_text = ""  # Clear after returning
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
