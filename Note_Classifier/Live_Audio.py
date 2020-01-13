import pyaudio
import sys
import struct
import pyqtgraph as pg
import numpy as np
import time
from scipy.fftpack import fft
from scipy.signal import blackmanharris, fftconvolve
from pyqtgraph.Qt import QtCore, QtGui
from DSP_Functions import Pitch_Tracker_Test

FS = 44100
chunk = 1024

notes = []

class PlotSig():
    def __init__(self):

        #Construct window and set up GUI
        self.trace = dict()
        pg.setConfigOptions(antialias = True)
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title = "waveform analyzer")
        self.win.setGeometry(5,115,1910,1070)

        #Bound and label Axes
        wf_xlabels = [(0, '0'), (2048, '2048'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        wf_ylabels = [(0, '0'), (127, '128'), (8000, '8000')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        #Adds waveform to plot
        self.waveform = self.win.addPlot(
        title = 'Waveform', row = 1, col = 1, axisitems ={'bottom': wf_xaxis, 'left': wf_yaxis},
        )

        #Initialize constants for use in capturing live audio
        self.chunk = 2048
        self.channels = 1
        self.rate = 48000
        self.note = 0
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunk)

        self.x = np.arange(0, 2*self.chunk, 2)
        self.f = np.linspace(0, self.rate / 2, self.chunk / 2)

        self.window = blackmanharris(self.chunk,False)

    def start(self):
        if(sys.flags.interactive != -1) or not hassattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec()

    def setData(self, name, x_data, y_data):

        if name in self.trace:
            self.trace[name].setData(x_data,y_data)
        else:
                self.trace[name] = self.waveform.plot(pen='c', width=3)
                self.waveform.setYRange(0, 275, padding=0)
                self.waveform.setXRange(0, 2 * self.chunk, padding=0.005)


    def update(self):
        #Streams live audio data
        wf_data = self.stream.read(self.chunk, exception_on_overflow = False)

        #Unpacks the collected data as a bit-stream
        wf_data = struct.unpack(str(self.chunk * 2) + 'B', wf_data)

        wf_data = np.array(wf_data, dtype='b')[::2] + 128
        self.setData(name = 'waveform', x_data = self.x, y_data =wf_data)

        wf_data = wf_data*self.window
        Spec_Dic = Pitch_Tracker_Test.spectral_properties(wf_data, self.rate)

        tunerNotes = Pitch_Tracker_Test.build_default_tuner_range()
        frequencies = np.array(sorted(tunerNotes.keys()))

        #input_note = round(Pitch_Tracker_Test.freq_from_autocorr(wf_data,self.rate),2)

            #if inputnote > frequencies[len(tunerNotes)-1]:                    #### not interested in notes above the notes list
            #        continue

            #if inputnote < frequencies[0]:                           #### not interested in notes below the notes list
            #        continue

            #if signal_level > soundgate:                                     #### basic noise gate to stop it guessing ambient noises
            #        continue



        #print(Spec_Dic.get('Q75'))

        #print(tunerNotes[targetnote])
        #targetnote = closest_value_index(frequencies, round(inputnote, 2))
        self.note = tunerNotes[frequencies[Pitch_Tracker_Test.closest_value_index(frequencies,round(Spec_Dic.get('IQR'),2))]]

        print(self.note)

        #signal_level = round(abs(loudness(raw_data_signal)),2)  #Find loudness of audio


    def animate(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(30)
        self.start()


if __name__ == '__main__':

    plot = PlotSig()
    plot.animate()
