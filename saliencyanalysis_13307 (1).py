
import pandas as pd
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from google.colab import drive
drive.mount('/content/drive')

#reading in csv
df_13307 = pd.read_csv('/content/drive/Shareddrives/Summer 2024 Project/MegaData/Combined_Data.csv')
df_13307.head()

df_13307.drop(columns=df_13307.columns[0], axis=1, inplace=True)
df_13307.head()

#removing last 4 columns

df_13307_remove4col = df_13307.drop('Standard Deviation', axis=1)
df_13307_remove4col = df_13307_remove4col.drop('Mean Curvature', axis=1)
df_13307_remove4col = df_13307_remove4col.drop('Largest Curvature', axis=1)
df_13307_remove4col = df_13307_remove4col.drop('Smallest Curvature', axis=1)
df_13307_remove4col

#classification MODEL

# separate features and target
X = df_13307_remove4col.drop('Binary Curvature', axis=1)
y = df_13307_remove4col['Binary Curvature']

# split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Sstandardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# creating neural network model
model = Sequential()
model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# compiling model (can change these)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# train the model (50 epochs)
model.fit(X_train, y_train, epochs=50, batch_size=10, verbose=1)

# evaluate the model
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f'Accuracy: {accuracy*100:.4f}%')

#FEATURE ANALYSIS

# function to compute gradients for saliency analysis
def compute_saliency_maps(model, X_input, class_idx):
    X_input = tf.convert_to_tensor(X_input)
    with tf.GradientTape() as tape:
        tape.watch(X_input)
        predictions = model(X_input)
        target_class = predictions[:, class_idx]  # class 1 for positive curvature
    gradients = tape.gradient(target_class, X_input)
    return gradients

# calculate saliency map for the test set
saliency_maps = compute_saliency_maps(model, X_test, class_idx=0)

saliency_map = np.abs(saliency_maps[0].numpy())  # absolute value of gradients
feature_names = X.columns

# plotting saliency map
plt.figure(figsize=(10, 6))
plt.bar(range(X_test.shape[1]), saliency_map, align="center")
plt.xticks(range(X_test.shape[1]), feature_names, rotation=90)
plt.title("Saliency Map for Binary Curvature Classification - 13307")
plt.tight_layout()
plt.show()

# printing the saliency values (if needed)
for i, feature in enumerate(feature_names):
    print(f"Feature {feature}: {saliency_map[i]}")

#notes:
#computes the saliency for a specific class
#this is more useful for classification tasks where looking for the importance of features related to one specific class label

# MATHEMATICAL EXPRESSION I

import statsmodels.api as sm

# extract the top features and target
X = df_13307_remove4col[['Maximum Degree', 'Laplacian Largest Eigenvalue']]
y = df_13307_remove4col['Diameter']

# add a constant for the intercept + fitting linear reg model
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()

print(model.summary())

# FORMULA -> Diameter = −3.5643 −3.2939(Maximum Degree) + 3.4189(Laplacian Largest Eigenvalue)

# MATHEMATICAL EXPRESSION II

import statsmodels.api as sm

# extract the top features and target
X = df_13307_remove4col[['Maximum Degree', 'Laplacian Largest Eigenvalue', 'Diameter']]
y = df_13307_remove4col['Binary Curvature']

# add a constant for the intercept + fitting linear reg model
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()

print(model.summary())

# FORMULA -> Diameter = −3.5643 −3.2939(Maximum Degree) + 3.4189(Laplacian Largest Eigenvalue)

# Formula --> Binary Curvature = 1.2299 - 0.0404(Max Degree) - 0.0612(LLE) - 0.0126(Diameter)
# 0.8513 = 1.2299 - 0.0404(3) - 0.0612(4) - 0.0126(1)
