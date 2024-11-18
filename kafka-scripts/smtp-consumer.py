import json
import numpy as np
import pandas as pd
from kafka import KafkaConsumer
import tensorflow as tf
from keras.models import Model
from keras.models import load_model

import matplotlib.pyplot as plt

# Kafka configuration
topic_name = "smta-cloud"
bootstrap_servers = "localhost:9092"

# Load the model
model_path = "your_model.h5"  # Replace with your actual model file path
model = load_model(model_path)

# Initialize Kafka consumer
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[bootstrap_servers],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
)

print(f"Listening to topic: {topic_name}")

# Function to save plot for each batch
def save_plot(train_close, valid_close, valid_predictions, batch_index):
    plt.figure(figsize=(16, 6))
    plt.title(f'Model Predictions - Batch {batch_index}', fontsize=20)
    plt.xlabel('Days', fontsize=14)
    plt.ylabel('Scaled Close Price', fontsize=14)
    plt.plot(train_close, label='Train Data')
    plt.plot(valid_close, label='Validation Data')
    plt.plot(valid_predictions, label='Predictions', linestyle='dashed')
    plt.legend(loc='lower right', fontsize=12)
    plot_filename = f'plot_batch_{batch_index}.png'
    plt.savefig(plot_filename)
    print(f"Saved plot for batch {batch_index} as {plot_filename}")
    plt.close()

# Simulated historical data for plotting (use real data in production)
historical_data = pd.DataFrame()  # Replace with your dataset for train/valid split
train_close = historical_data['Close'][:5000].values if not historical_data.empty else []

batch_index = 1

# Process messages
for message in consumer:
    batch = np.array(message.value)  # Deserialize JSON to NumPy array
    print(f"Received batch {batch_index} with shape: {batch.shape}")
    
    # Reshape batch for model input
    batch = batch.reshape(batch.shape[0], batch.shape[1], 1)
    
    # Predict
    predictions = model.predict(batch)
    
    # Create simulated validation data for the plot (real data should match your application)
    valid_close = np.linspace(0.5, 1, len(predictions))  # Replace with actual validation data
    valid_predictions = predictions.flatten()

    # Save the plot
    save_plot(train_close, valid_close, valid_predictions, batch_index)
    
    batch_index += 1