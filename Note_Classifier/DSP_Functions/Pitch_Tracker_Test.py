import sys
import wave
import numpy as np
from scipy.signal import fftconvolve
from aubio import source, pitch

#Source https://stackoverflow.com/questions/54612204/trying-to-get-the-frequencies-of-a-wav-file-in-python
def spectral_properties(y: np.ndarray, fs: int) -> dict:

    #Calculates the Fast Fourier Transform of the signal
    spec = np.abs(np.fft.rfft(y))
    freq = np.fft.rfftfreq(len(y), d=1 / fs)
    max_freq = np.argsort(spec)
    spec = np.abs(spec)

    #Calculates the average amplitude of the signal
    amp = spec / spec.sum()
    mean = (freq * amp).sum()
    sd = np.sqrt(np.sum(amp * ((freq - mean) ** 2)))

    #Perfoms a cumulative sum of all the data passed in thus far
    amp_cumsum = np.cumsum(amp)
    median = freq[len(amp_cumsum[amp_cumsum <= 0.5]) + 1]
    mode = freq[amp.argmax()]

    #Calculates the 25th anf 75th Quartiles
    Q25 = freq[len(amp_cumsum[amp_cumsum <= 0.25]) + 1]
    Q75 = freq[len(amp_cumsum[amp_cumsum <= 0.75]) + 1]

    #Finds the Interquartile Range of the FFT
    IQR = Q75 - Q25
    z = amp - amp.mean()
    w = amp.std()
    skew = ((z ** 3).sum() / (len(spec) - 1)) / w ** 3
    kurt = ((z ** 4).sum() / (len(spec) - 1)) / w ** 4

    result_d = {
        'max_freq': max_freq[0],
        'mean': mean,
        'sd': sd,
        'median': median,
        'mode': mode,
        'Q25': Q25,
        'Q75': Q75,
        'IQR': IQR,
        'skew': skew,
        'kurt': kurt
    }

    return result_d

def find_nearest(array, value):
    index = (np.abs(array - value)).argmin()
    return array[index]

def closest_value_index(array, guessValue):
    # Find closest element in the array, value wise
    closestValue = find_nearest(array, guessValue)
    # Find indices of closestValue
    indexArray = np.where(array==closestValue)
    # Numpys 'where' returns a 2D array with the element index as the value
    return indexArray[0][0]

# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def parabolic(f, x):
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)

# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def freq_from_autocorr(raw_data_signal, fs):
    corr = fftconvolve(raw_data_signal, raw_data_signal[::-1], mode='full')
    corr = corr[len(corr)/2:]
    d = diff(corr)
    start = find(d > 0)[0]
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)
    return fs / px

def build_default_tuner_range():

    return {65.41:'C2',
            69.30:'C2#',
            73.42:'D2',
            77.78:'E2b',
            82.41:'E2',
            87.31:'F2',
            92.50:'F2#',
            98.00:'G2',
            103.80:'G2#',
            110.00:'A2',
            116.50:'B2b',
            123.50:'B2',
            130.80:'C3',
            138.60:'C3#',
            146.80:'D3',
            155.60:'E3b',
            164.80:'E3',
            174.60:'F3',
            185.00:'F3#',
            196.00:'G3',
            207.70:'G3#',
            220.00:'A3',
            233.10:'B3b',
            246.90:'B3',
            261.60:'C4',
            277.20:'C4#',
            293.70:'D4',
            311.10:'E4b',
            329.60:'E4',
            349.20:'F4',
            370.00:'F4#',
            392.00:'G4',
            415.30:'G4#',
            440.00:'A4',
            466.20:'B4b',
            493.90:'B4',
            523.30:'C5',
            554.40:'C5#',
            587.30:'D5',
            622.30:'E5b',
            659.30:'E5',
            698.50:'F5',
            740.00:'F5#',
            784.00:'G5',
            830.60:'G5#',
            880.00:'A5',
            932.30:'B5b',
            987.80:'B5',
            1047.00:'C6',
            1109.0:'C6#',
            1175.0:'D6',
            1245.0:'E6b',
            1319.0:'E6',
            1397.0:'F6',
            1480.0:'F6#',
            1568.0:'G6',
            1661.0:'G6#',
            1760.0:'A6',
            1865.0:'B6b',
            1976.0:'B6',
            2093.0:'C7'
            }
