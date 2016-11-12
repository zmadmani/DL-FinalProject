import sys
import os
import numpy as np
from scipy.io.wavfile import read

#dir = "C:\\Users\\zaina\\Desktop\\School\\Master Year\\Deep Learning\\Final Project\\wav_dataset\\ds_chunked\\"
dir = "./ds_chunked/"

def pad(content, req_len=48000):
	padded = np.zeros((req_len), dtype=float)
	padded[:content.shape[0]] = content
	return padded

onlyfiles = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
dataset = np.zeros(shape=(len(onlyfiles),10,4800))
for i in range(len(onlyfiles)):
	file = onlyfiles[i]
	a = read(dir + file)
	content = np.array(a[1],dtype=float)
	if(len(content) != 48000):
		content = pad(content)
	datapoint = np.zeros(shape=(10,4800))
	for i in range(10):
		slice = content[i*4800:(i+1)*4800]
		if(np.max(np.abs(slice)) > 0):
			datapoint[i] = np.int16(slice/np.max(np.abs(slice)) * 32767)
		else:
			datapoint[i] = np.zeros(shape=(4800))

	dataset[i] = datapoint
	
np.save("./dataset.npy",dataset)