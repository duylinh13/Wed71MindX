import tkinter as tk
from tkinter import filedialog
import speech_recognition as sr
from io import BytesIO
import threading
import pyttsx3
from gtts import gTTS
import pygame

class SpeechRecorder:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.volume = 2  # Giá trị âm lượng mặc định
        self.rate = 200    # Tốc độ mặc định (từ 0 đến 400)
        self.recording = False
        self.convert_after_stop = False
        self.recognizer = sr.Recognizer()
        self.recorded_audio = None

    def start_recording(self):
        self.recording = True
        start_button.config(state=tk.DISABLED, bg="#4CAF50", fg="white", font=("Arial", 12))
        stop_button.config(state=tk.NORMAL, bg="#DC143C", fg="white", font=("Arial", 12))

        def listen_audio():
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Adjusting noise...")

                try:
                    self.recorded_audio = self.recognizer.listen(source, timeout=4)
                    text = self.recognizer.recognize_google(self.recorded_audio, language="vi-VN")
                    print("Decoded Text: {}".format(text))
                    text_entry.delete("1.0", tk.END)
                    text_entry.insert(tk.END, text)

                except sr.WaitTimeoutError:
                    print("Timed out waiting for phrase to start")
                    text_entry.delete("1.0", tk.END)
                    text_entry.insert(tk.END, "No sound detected")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    text_entry.delete("1.0", tk.END)
                    text_entry.insert(tk.END, "Could not understand audio")
                finally:
                    self.recording = False
                    start_button.config(state=tk.NORMAL, bg="#00FFFF", fg="black", font=("Arial", 12))
                    stop_button.config(state=tk.DISABLED, bg="#DC143C", fg="white", font=("Arial", 12))

                    if self.convert_after_stop:
                        self.convert_after_stop = False
                        self.text_to_speech()

        threading.Thread(target=listen_audio).start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            text_entry.delete("1.0", tk.END)
            text_entry.insert(tk.END, "Recording stopped")
            start_button.config(state=tk.NORMAL, bg="#00FFFF", fg="black", font=("Arial", 12))
            stop_button.config(state=tk.DISABLED, bg="#DC143C", fg="white", font=("Arial", 12))

    def text_to_speech(self, text=None, female_voice=False):
        if text is None:
            text = text_entry.get("1.0", tk.END).strip()

        if female_voice:
            tts = gTTS(text=text, lang='vi', slow=False)  # slow=False: đảm bảo giọng nữ được phát với tốc độ bình thường
            audio_stream = BytesIO()
            tts.write_to_fp(audio_stream)
            audio_stream.seek(0)

            pygame.mixer.init()
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()

        else:
            self.engine.setProperty('volume', self.volume)
            self.engine.setProperty('rate', self.rate)  # Đặt tốc độ
            self.engine.say(text)
            self.engine.runAndWait()

    def load_text_file(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                text_entry.delete("1.0", tk.END)
                text_entry.insert(tk.END, text)

    def set_volume(self, volume):
        self.volume = volume
        self.engine.setProperty('volume', volume)

    def set_rate(self, rate):
        self.rate = rate

root = tk.Tk()
root.title("Speech to Text & Text to Speech")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

text_entry = tk.Text(frame, width=60, height=5)
text_entry.grid(row=0, column=0, padx=5, pady=5, columnspan=4)

recorder = SpeechRecorder()

start_button = tk.Button(frame, text="Start Recording", command=recorder.start_recording, bg="#4CAF50", fg="white", font=("Arial", 12))
start_button.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

stop_button = tk.Button(frame, text="Stop Recording", command=recorder.stop_recording, state=tk.DISABLED, bg="#DC143C", fg="white", font=("Arial", 12))
stop_button.grid(row=1, column=2, padx=5, pady=5, columnspan=2)

convert_button = tk.Button(frame, text="Convert to Speech (Male)", command=lambda: recorder.text_to_speech(female_voice=False), bg="#008CBA", fg="white", font=("Arial", 12))
convert_button.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

convert_button_female = tk.Button(frame, text="Convert to Speech (Female)", command=lambda: recorder.text_to_speech(female_voice=True), bg="#008CBA", fg="white", font=("Arial", 12))
convert_button_female.grid(row=2, column=2, padx=5, pady=5, columnspan=2)

volume_scale = tk.Scale(frame, from_=0.1, to=1, resolution=0.1, orient=tk.HORIZONTAL, label="Volume", command=lambda volume: recorder.set_volume(float(volume)))
volume_scale.grid(row=3, column=0, padx=5, pady=5, columnspan=4)

rate_scale = tk.Scale(frame, from_=2, to=400, orient=tk.HORIZONTAL, label="Rate", command=lambda rate: recorder.set_rate(int(rate)))
rate_scale.grid(row=4, column=0, padx=5, pady=5, columnspan=4)

load_button = tk.Button(frame, text="Load Text File", command=recorder.load_text_file, bg="#FFD700", fg="black", font=("Arial", 12))
load_button.grid(row=5, column=0, padx=5, pady=5, columnspan=4)

root.mainloop()
