from pydub import AudioSegment
from pydub.utils import make_chunks

output_dir = "chunked/"
myaudio = AudioSegment.from_file("Classical Music for Studying and Concentration  Chopin Piano Music to Study and Concentrate.wav" , "wav") 
chunk_length_ms = 1000*10 # pydub calculates in millisec
chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of one sec

#Export all of the individual chunks as wav files
for i, chunk in enumerate(chunks):
    chunk_name = "chunk{0}.wav".format(i)
    print("exporting", chunk_name)
    chunk.export(output_dir + chunk_name, format="wav")