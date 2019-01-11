#!/usr/bin/env python3


import pyaudio, wave

import unittest
import socket
import threading

from __init__ import *

HOST = '192.168.1.46'
PORT = 8045
# Using an image for tests, though this will primarily be used for audio
FILENAME = 'image.jpg'
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 4

class MyImageClient():
  def __init__(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    chunk_number = 1
    with open(FILENAME, "rb") as f:
      chunk = f.read(CHUNK_SIZE)
      while chunk:
        s.send(chunk)
        chunk_number += 1
        chunk = f.read(CHUNK_SIZE)

    s.close()

class MyAudioClient():
  def __init__(self):
    p = pyaudio.PyAudio()
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)
    
    print("* recording")
    
    frames = []
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
        data = stream.read(CHUNK_SIZE)
        #frames.append(data)
        s.send(data)
    
    print("* done recording")
    
    stream.stop_stream()
    stream.close()
    p.terminate()

class MyServerTests(unittest.TestCase):
  def __init__(self):
    #self.thread = threading.Thread(target=server_up)
    #self.test_is_up()
    self.client = MyAudioClient()
    #self.test_is_down()
  
  def test_is_up(self):
    self.thread.start() 
    #self.assertEqual(server_up(), 'The server is UP')

  def test_is_down(self):
    self.thread.join() 

if __name__ == '__main__':
  test = MyServerTests()
