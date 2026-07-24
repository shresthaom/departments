import csv
from logistic_regression import LogisticRegression

# store the training data
X = []
Y = []

# read the training dataset
with open("training_dataset.csv", "r") as file:

    reader = csv.reader(file)

    next(reader)

    # read each row from the dataset
    for row in reader:

        features = [
            float(row[0]),  # Age
            float(row[1]),  # Date.diff
            float(row[2]),  # DayOfWeek
            float(row[3]),  # PreviousMissed
            float(row[4]),  # PreviousCompleted
        ]

        target = int(row[5])

        X.append(features)
        Y.append(target)


# find the minimum and maximum values
age_values = [row[0] for row in X]
date_diff_values = [row[1] for row in X]
day_values = [row[2] for row in X]
missed_values = [row[3] for row in X]
completed_values = [row[4] for row in X]

min_age = min(age_values)
max_age = max(age_values)

min_date = min(date_diff_values)
max_date = max(date_diff_values)

min_day = min(day_values)
max_day = max(day_values)

min_missed = min(missed_values)
max_missed = max(missed_values)

min_completed = min(completed_values)
max_completed = max(completed_values)


# normalize the training data
for row in X:

    row[0] = (row[0] - min_age) / (max_age - min_age)
    row[1] = (row[1] - min_date) / (max_date - min_date)
    row[2] = (row[2] - min_day) / (max_day - min_day)
    row[3] = (row[3] - min_missed) / (max_missed - min_missed)
    row[4] = (row[4] - min_completed) / (max_completed - min_completed)


# create the logistic regression model
model = LogisticRegression()

# train the model
model.train(X, Y)


# store the testing data
X_test = []
Y_test = []

# read the testing dataset
with open("testing_dataset.csv", "r") as file:

    reader = csv.reader(file)

    next(reader)

    # read each row from the dataset
    for row in reader:

        features = [
            float(row[0]),  # Age
            float(row[1]),  # Date.diff
            float(row[2]),  # DayOfWeek
            float(row[3]),  # PreviousMissed
            float(row[4]),  # PreviousCompleted
        ]

        target = int(row[5])

        X_test.append(features)
        Y_test.append(target)


# normalize the testing data using the training min and max values
for row in X_test:

    row[0] = (row[0] - min_age) / (max_age - min_age)
    row[1] = (row[1] - min_date) / (max_date - min_date)
    row[2] = (row[2] - min_day) / (max_day - min_day)
    row[3] = (row[3] - min_missed) / (max_missed - min_missed)
    row[4] = (row[4] - min_completed) / (max_completed - min_completed)


# calculate accuracy
accuracy = model.accuracy(X_test, Y_test)
print(f"Accuracy: {accuracy * 100:.2f}%")

# save the learned weights
model.save_weights("weights.txt")
with open("normalization.txt", "w") as file:

    file.write(str(min_age) + "\n")
    file.write(str(max_age) + "\n")

    file.write(str(min_date) + "\n")
    file.write(str(max_date) + "\n")

    file.write(str(min_day) + "\n")
    file.write(str(max_day) + "\n")

    file.write(str(min_missed) + "\n")
    file.write(str(max_missed) + "\n")

    file.write(str(min_completed) + "\n")
    file.write(str(max_completed) + "\n")

print("Weights:", model.weights)
print("Bias:", model.bias)

# confusion matrix
tp = 0
tn = 0
fp = 0
fn = 0

for i in range(len(X_test)):

    prediction = model.predict(X_test[i])

    if prediction == 1 and Y_test[i] == 1:
        tp += 1

    elif prediction == 0 and Y_test[i] == 0:
        tn += 1

    elif prediction == 1 and Y_test[i] == 0:
        fp += 1

    else:
        fn += 1

print("\nConfusion Matrix")
print("----------------------------")
print("True Positive :", tp)
print("True Negative :", tn)
print("False Positive:", fp)
print("False Negative:", fn)

precision = tp / (tp + fp)

recall = tp / (tp + fn)

f1_score = 2 * precision * recall / (precision + recall)

print("\nPerformance Metrics")
print("----------------------------")
print(f"Accuracy : {accuracy * 100:.2f}%")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall   : {recall * 100:.2f}%")
print(f"F1-Score : {f1_score * 100:.2f}%")

print("\nPredicted no-shows:", tp + fp)
print("Total test samples:", len(X_test))