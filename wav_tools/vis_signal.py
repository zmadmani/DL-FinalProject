from scipy import signal
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import numpy as np

file = read("./ds_chunk1.wav")[1]

print(len(file))

fs = 10e3
N = 1e5
amp = 2 * np.sqrt(2)
noise_power = 0.001 * fs / 2
time = np.arange(N) / fs
freq = np.linspace(1e2, 1e3, N)
x = amp * np.sin(2*np.pi*freq*time)
x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
print(file)
f, t, Sxx = signal.spectrogram(x, fs)
plt.pcolormesh(t, f, Sxx)
plt.ylabel('Freq [Hz]')
plt.xlabel('Time [sec]')
plt.show()