from logistic_regression import LogisticRegression

# create the logistic regression model
model = LogisticRegression()

# load the learned weights
model.load_weights("weights.txt")
with open("normalization.txt", "r") as file:

    values = [float(line.strip()) for line in file]

min_age = values[0]
max_age = values[1]

min_date = values[2]
max_date = values[3]

min_day = values[4]
max_day = values[5]

min_missed = values[6]
max_missed = values[7]

min_completed = values[8]
max_completed = values[9]

# new patient data
age = 32
date_diff = 15
day_of_week = 3
previous_missed = 0
previous_completed = 2

age = (age - min_age) / (max_age - min_age)

date_diff = (date_diff - min_date) / (max_date - min_date)

day_of_week = (day_of_week - min_day) / (max_day - min_day)

previous_missed = (
    (previous_missed - min_missed)
    / (max_missed - min_missed)
)

previous_completed = (
    (previous_completed - min_completed)
    / (max_completed - min_completed)
)


features = [
    age,
    date_diff,
    day_of_week,
    previous_missed,
    previous_completed
]

# calculate the no-show probability
probability = model.predict_probability(features)

# predict whether the patient will no-show
prediction = model.predict(features)

print(f"No Show Probability: {probability * 100:.2f}%")

if prediction == 1:
    print("Prediction: Patient is likely to miss the appointment.")
else:
    print("Prediction: Patient is likely to attend the appointment.")