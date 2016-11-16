import sys
import os
import numpy as np
from scipy.io.wavfile import read

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
dir = ROOT_DIR + "/chunked_downsampled_wavfiles/"
LEN_SAMPLE = 30
BITRATE = 4800
LEN_TIMESTEP = 0.5

def pad(content, req_len=BITRATE*LEN_SAMPLE):
	padded = np.zeros((req_len), dtype=float)
	padded[:content.shape[0]] = content
	return padded

onlyfiles = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
dataset = np.zeros(shape=(len(onlyfiles),int(LEN_SAMPLE/LEN_TIMESTEP),int(BITRATE*LEN_TIMESTEP)))
for i in range(len(onlyfiles)):
	file = onlyfiles[i]
	a = read(dir + file)
	content = np.array(a[1],dtype=float)
	if(len(content) != BITRATE*LEN_SAMPLE):
		content = pad(content)
	datapoint = np.zeros(shape=(int(LEN_SAMPLE/LEN_TIMESTEP),int(BITRATE*LEN_TIMESTEP)))
	for i in range(int(LEN_SAMPLE/LEN_TIMESTEP)):
		slice = content[i*int(BITRATE*LEN_TIMESTEP):(i+1)*int(BITRATE*LEN_TIMESTEP)]
		if(np.max(np.abs(slice)) > 0):
			datapoint[i] = np.int16(slice/np.max(np.abs(slice)) * 32767)
		else:
			datapoint[i] = np.zeros(shape=(int(BITRATE*LEN_TIMESTEP)))

	dataset[i] = datapoint

np.save("./dataset.npy",dataset)
