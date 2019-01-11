#!/usr/bin/env python3

# Thanks to
# https://gist.github.com/rambabusaravanan/a0811f8c9bff440f06ca04d06abdd363#file-client-py-L4 
# https://stackoverflow.com/questions/35344649/reading-input-sound-signal-using-python
import os
import socket
import time

import numpy as np
import scipy.io.wavfile
import math

from random import randint

import pyaudio
import wave

import speech_recognition as sr

from threading import Thread, Lock, Event
from mycroft.stt import STTFactory
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message


HOST = '0.0.0.0'
PORT = 8045
FILENAME = 'received.tmp'
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

ws = None

config = ConfigurationManager.get()

def connect():
    ws.run_forever()

def server_up():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((HOST, PORT))
  s.listen(1)

  frames = []
  p = pyaudio.PyAudio()
  
  while True:
    conn, addr = s.accept()
    print('Incoming client transfer accepted ', addr)
    if os.path.exists(FILENAME):
      os.remove(FILENAME)
    while True:
      try:
        data_in = conn.recv(CHUNK_SIZE)
        if not data_in: 
          print('Transfer ended')
          transmission_end(conn, p, frames)
          break
        frames.append(data_in)
      except (socket.error):
        print('Client connection closed', addr)
        break

  transmission_end(conn, p, frames)

def transmission_end(conn, p, frames):
  conn.close()
  global ws
  global config
  ws = WebsocketClient()
  wf = wave.open(FILENAME, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(RATE)
  wf.writeframes(b''.join(frames))
  wf.close()
  stt_as_service()
  #fc = FileConsumer(file_location=FILENAME, emitter=ws)
  #fc.audio_to_stt()

def stt_as_service():
  config = ConfigurationManager.get()
  ConfigurationManager.init(ws)
  event_thread = Thread(target=connect)
  event_thread.setDaemon(True)
  event_thread.start()
  config = config.get("wav_client", {"path": FILENAME})
  try:
    file_consumer = FileConsumer(file_location=config["path"], emitter=ws)
    file_consumer.start()
    while True:
      time.sleep(100)
  except KeyboardInterrupt, e:
    LOG.exception(e)
    file_consumer.stop()
    file_consumer.join()
    sys.exit()

def read_wave_file(wave_file_path):
  '''
  reads the wave file at provided path and return the expected
  Audio format
  '''
  # use the audio file as the audio source
  r = sr.Recognizer()
  with sr.AudioFile(wave_file_path) as source:
    audio = r.record(source)
  return audio

class FileConsumer(Thread):
  def __init__(self, file_location=FILENAME, emitter=None):
    super(FileConsumer, self).__init__()
    self.path = file_location
    self.stop_event = Event()
    self.stt = None
    self.emitter = emitter



  def audio_to_stt(self):
    self.stt = STTFactory.create()
    audio = read_wave_file(FILENAME)
    text = self.stt.execute(audio).lower().strip()
    self.emitter.on("stt.request", self.handle_external_request)
    self.emitter.emit(
      Message("recognizer_loop:utterance", 
      {"utterances": [text]},
      {"source": "wav_client"}))

  def handle_external_request(self, message):
    file = message.data.get("File")
    if self.stt is None:
      error = "STT initialization failure"
      self.emitter.emit(
          Message("stt.error", {"error": error}))
    elif not file:
      error = "No file provided for transcription"
      self.emitter.emit(
          Message("stt.error", {"error": error}))
    elif not exists(file):
      error = "Invalid file path provided for transcription"
      self.emitter.emit(
          Message("stt.error", {"error": error}))
    else:
      audio = read_wave_file(file)
      transcript = self.stt.execute(audio).lower().strip()
      self.emitter.emit(Message("stt.reply",
                                {"transcription": transcript}))

if __name__ == '__main__':
  server_up()
