from pydub import AudioSegment
from pydub.utils import make_chunks
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

input_dir = ROOT_DIR + "/downsampled_wavfiles"
output_dir = ROOT_DIR + "/chunked_downsampled_wavfiles"

onlyfiles = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
for file in onlyfiles:
    myaudio = AudioSegment.from_file(input_dir + "/" + file , "wav")
    chunk_length_ms = 1000*3600 # pydub calculates in millisec
    chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of one sec

    #Export all of the individual chunks as wav files
    for i, chunk in enumerate(chunks):
        chunk_name = "/chunk{0}.wav".format(i)
        print("exporting", chunk_name)
        chunk.export(output_dir + chunk_name, format="wav")
