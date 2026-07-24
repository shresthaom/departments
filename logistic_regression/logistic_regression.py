import math


class LogisticRegression:

    def __init__(self, learning_rate=0.01, epochs=1000):

        self.learning_rate = learning_rate
        self.epochs = epochs

        # weights for the input features
        self.weights = []

        # bias value
        self.bias = 0

    # convert any value into a probability between 0 and 1
    def sigmoid(self, z):

        return 1 / (1 + math.exp(-z)) 

    # calculate the probability for one data sample
    def predict_probability(self, features):

        z = self.bias

        for i in range(len(features)):
            z += self.weights[i] * features[i]

        return self.sigmoid(z)  
       
     # train the model using gradient descent
    def train(self, X, Y):

        # initialize one weight for each feature
        self.weights = [0] * len(X[0])

        # initialize bias
        self.bias = 0

        # repeat training for the given number of epochs
        for epoch in range(self.epochs):

            # go through every training sample
            for i in range(len(X)):

                prediction = self.predict_probability(X[i])

                error = prediction - Y[i]  #Y[i] is the no show value

                # update each weight
                for j in range(len(self.weights)):

                    self.weights[j] -= (
                        self.learning_rate
                        * error
                        * X[i][j]
                    )

                # update bias
                self.bias -= self.learning_rate * error

    # predict whether the patient will no show
    def predict(self, features):

        probability = self.predict_probability(features)

        if probability >= 0.5:
            return 1

        return 0     

# calculate the accuracy of the model
    def accuracy(self, X, Y):

        correct = 0

        for i in range(len(X)):

            prediction = self.predict(X[i])

            if prediction == Y[i]:
                correct += 1

        return correct / len(X)  

    # save the learned weights and bias
    def save_weights(self, filename):

        with open(filename, "w") as file:

            for weight in self.weights:
                file.write(str(weight) + "\n")

            file.write(str(self.bias))         

        # load the learned weights and bias
    def load_weights(self, filename):

        with open(filename, "r") as file:

            values = [line.strip() for line in file if line.strip()]

        self.weights = []

        for value in values[:-1]:
            self.weights.append(float(value))

        self.bias = float(values[-1])