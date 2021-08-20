import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class UnivariateLinearRegression:

	def __init__(self, learning_rate=0.001, iterations=100, random_state=None):

		np.random.seed(random_state)
		self.weight = np.random.uniform(-10, 10)		# Weight initialization.
		self.bias = np.random.uniform(-10, 10)			# Bias initialization.
		self.learning_rate = learning_rate
		self.iterations = iterations

	# Use this if the X and y are already separated from each other.
	def take_data_raw(self, X, y):
		self.X = X
		self.y = y

		self.n_samples = len(self.X)
	
	# Use this only when the first column of the csv file is the X
	# and when the second column contains the y values.
	def take_data_csv(self, csv_file):
		df = pd.read_csv(csv_file)
		self.X = df.iloc[:,0]
		self.y = df.iloc[:,1]

		self.n_samples = len(self.X)

	def mse(self, y, y_hat):
		return np.sum((y-y_hat)**2)

	def train(self):
		self.updated_weight = self.weight
		self.updated_bias = self.bias

		self.errors = []

		for i in range(self.iterations):
			y_hat = self.updated_weight*self.X + self.updated_bias

			# y_hat adalah hasil prediksi berupa array.
			error = self.mse(self.y, y_hat)
			self.errors.append(error)

			self.d_weight = (-2/self.n_samples) * np.sum(self.X * (self.y-y_hat))
			self.d_bias = (-2/self.n_samples) * np.sum(self.y - y_hat)

			self.updated_weight = self.updated_weight - (self.learning_rate*self.d_weight)
			self.updated_bias = self.updated_bias - (self.learning_rate*self.d_bias)

	def plot_before(self):
		plt.scatter(self.X, self.y)
		
		x_line = np.linspace(self.X.min(), self.X.max(), 100)
		y_line = self.weight*x_line + self.bias
		plt.plot(x_line, y_line)
		plt.show()

	def plot_after(self):
		plt.scatter(self.X, self.y)
		
		x_line = np.linspace(self.X.min(), self.X.max(), 1000)
		y_line = self.updated_weight*x_line + self.updated_bias
		plt.plot(x_line, y_line)
		plt.show()

	def plot_errors(self):
		plt.plot(self.errors)
		plt.xlabel('Iterations')
		plt.ylabel('Error')
		plt.show()