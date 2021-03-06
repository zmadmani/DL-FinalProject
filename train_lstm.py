"""
Text generation using a Recurrent Neural Network (LSTM).
"""


import tensorflow as tf
import numpy as np
import random
import time
import sys
from scipy.io.wavfile import write



## RNN with num_layers LSTM layers and a fully-connected output layer
## The network allows for a dynamic number of iterations, depending on the inputs it receives.
##
##    out   (fc layer; out_size)
##     ^
##    lstm
##     ^
##    lstm  (lstm size)
##     ^
##     in   (in_size)
class ModelNetwork:
	def __init__(self, in_size, lstm_size, num_layers, out_size, session, learning_rate=0.003, name="rnn"):
		self.scope = name

		self.in_size = in_size
		self.lstm_size = lstm_size
		self.num_layers = num_layers
		self.out_size = out_size

		self.session = session

		self.learning_rate = tf.constant( learning_rate )

		# Last state of LSTM, used when running the network in TEST mode
		self.lstm_last_state = np.zeros((self.num_layers*2*self.lstm_size,))

		with tf.variable_scope(self.scope):
			## (batch_size, timesteps, in_size)
			self.xinput = tf.placeholder(tf.float32, shape=(None, None, self.in_size), name="xinput")
			self.lstm_init_value = tf.placeholder(tf.float32, shape=(None, self.num_layers*2*self.lstm_size), name="lstm_init_value")

			# LSTM
			# TODO: migrate to state_is_tuple = True
			self.lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.lstm_size, forget_bias=1.0, state_is_tuple=False)
			self.lstm = tf.nn.rnn_cell.MultiRNNCell([self.lstm_cell] * self.num_layers)

			# Iteratively compute output of recurrent network
			outputs, self.lstm_new_state = tf.nn.dynamic_rnn(self.lstm, self.xinput, initial_state=self.lstm_init_value)

			# Linear activation (FC layer on top of the LSTM net)
			self.rnn_out_W = tf.Variable(tf.random_normal( (self.lstm_size, self.out_size), stddev=0.01 ))
			self.rnn_out_B = tf.Variable(tf.random_normal( (self.out_size, ), stddev=0.01 ))

			outputs_reshaped = tf.reshape( outputs, [-1, self.lstm_size] )
			network_output = ( tf.matmul( outputs_reshaped, self.rnn_out_W ) + self.rnn_out_B )

			batch_time_shape = tf.shape(outputs)
			self.final_outputs = tf.reshape(network_output, (batch_time_shape[0], batch_time_shape[1], self.out_size) )

			## Training: provide target outputs for supervised training.
			self.y_batch = tf.placeholder(tf.float32, (None, None, self.out_size))
			y_batch_long = tf.reshape(self.y_batch, [-1, self.out_size])

			#self.cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(network_output, y_batch_long) )
			self.cost = tf.reduce_mean(tf.nn.l2_loss(tf.sub(network_output, y_batch_long)))
			self.train_op = tf.train.RMSPropOptimizer(self.learning_rate, 0.9).minimize(self.cost)


	## Input: X is a single element, not a list!
	def run_step(self, x, init_zero_state=True):
		## Reset the initial state of the network.
		if init_zero_state:
			init_value = np.zeros((self.num_layers*2*self.lstm_size,))
		else:
			init_value = self.lstm_last_state

		out, next_lstm_state = self.session.run([self.final_outputs, self.lstm_new_state], feed_dict={self.xinput:[x], self.lstm_init_value:[init_value]   } )

		self.lstm_last_state = next_lstm_state[0]

		return out[0][0]


	## xbatch must be (batch_size, timesteps, input_size)
	## ybatch must be (batch_size, timesteps, output_size)
	def train_batch(self, xbatch, ybatch):
		init_value = np.zeros((xbatch.shape[0], self.num_layers*2*self.lstm_size))

		cost, _ = self.session.run([self.cost, self.train_op], feed_dict={self.xinput:xbatch, self.y_batch:ybatch, self.lstm_init_value:init_value   } )

		return cost


ckpt_file = ""
TEST_PREFIX = np.array([[[0]*2400]])

print "Usage:"
print '\t\t ', sys.argv[0], ' [ckpt model to load] [prefix, e.g., "The "]'
if len(sys.argv)>=2:
	ckpt_file=sys.argv[1]
if len(sys.argv)==3:
	TEST_PREFIX = sys.argv[2]


## Convert to 1-hot coding
# vocab = list(set(data_))

data = np.load("./dataset.npy")
print(data.shape)
exit()
TEST_PREFIX = data[random.randint(0,1083),:3]
print(TEST_PREFIX.shape)

in_size = out_size = 2400
lstm_size = 512 #128
num_layers = 2
batch_size = 32
time_steps = 59 #50

NUM_TRAIN_BATCHES = 20000

LEN_TEST_TEXT = 20 # Number of test characters of text to generate after training the network



## Initialize the network
config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.InteractiveSession(config=config)

net = ModelNetwork(in_size = in_size,
					lstm_size = lstm_size,
					num_layers = num_layers,
					out_size = out_size,
					session = sess,
					learning_rate = 0.0001,
					name = "char_rnn_network")

sess.run( tf.initialize_all_variables() )

saver = tf.train.Saver(tf.all_variables())



## 1) TRAIN THE NETWORK
if ckpt_file == "":
	last_time = time.time()

	batch = np.zeros((batch_size, time_steps, in_size))
	batch_y = np.zeros((batch_size, time_steps, in_size))

	possible_batch_ids = range(data.shape[0]-time_steps-1)
	for i in range(NUM_TRAIN_BATCHES):
		# Sample time_steps consecutive samples from the dataset text file
		batch_id = random.sample( possible_batch_ids, batch_size )

		for j in range(time_steps):
			batch[:, j, :] = data[batch_id, j, :]
			batch_y[:, j, :] = data[batch_id, j+1, :]

		cst = net.train_batch(batch, batch_y)

		if (i%100) == 0:
			new_time = time.time()
			diff = new_time - last_time
			last_time = new_time
			print "batch: ",i,"   loss: ",cst,"   speed: ",(100.0/diff)," batches / s"
		if (i%1000) == 0:
			gen = TEST_PREFIX
			out = np.array([net.run_step(TEST_PREFIX[0], True)])
			for j in range(LEN_TEST_TEXT):
				gen = np.append(gen, out)
				out = net.run_step(out, False)
				out = np.array([out])
			scaled = np.int16(gen/np.max(np.abs(gen)) * 32767)
			write('test' + str(i) + ".wav", 4800, scaled)
	saver.save(sess, "model.ckpt")


## 2) GENERATE LEN_TEST_TEXT CHARACTERS USING THE TRAINED NETWORK

if ckpt_file != "":
	saver.restore(sess, ckpt_file)

for i in range(len(TEST_PREFIX)):
	out = np.array([net.run_step([TEST_PREFIX[i]], i==0)])

print "GENERATING"
gen = TEST_PREFIX
for i in range(LEN_TEST_TEXT):
	#element = np.random.choice( range(len(vocab)), p=out ) # Sample character from the network according to the generated output probabilities
	gen = np.append(gen, out)
	out = net.run_step(out , False )
	out = np.array([out])
scaled = np.int16(gen/np.max(np.abs(gen)) * 32767)
write('test.wav', 4800, scaled)
