from scipy.io.wavfile import read
import numpy as np
import matplotlib.pyplot as plt

a = read("sine.wav")
arr = np.array(a[1],dtype=float)
print(len(arr[::100]))

plt.plot(range(len(arr[::100])),arr[::100])
plt.show()
