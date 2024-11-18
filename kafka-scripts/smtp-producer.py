import pandas as pd
import numpy as np
from time import sleep
import json
from kafka import KafkaProducer, KafkaAdminClient, NewTopic

# Kafka configuration
topic_name = "smta-cloud"
partitions = 1
replication = 1
bootstrap_servers = "localhost:9092"

# Initialize Kafka admin client
admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

# Create topic if not exists
if topic_name not in admin_client.list_topics():
    new_topic = NewTopic(
        name=topic_name, num_partitions=partitions, replication_factor=replication
    )
    admin_client.create_topics(new_topics=[new_topic])

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[bootstrap_servers],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

# Read CSV and process data
file_path = '/mnt/data/SPX.csv'
data = pd.read_csv(file_path)

# Extract Close column and start from record 5000
data = data.iloc[5000:]
close_values = data['Close'].values

# Scale data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(close_values.reshape(-1, 1))

# Prepare test set
test_data = scaled_data[:120 * 5, :]  # Simulating records after index 5000
x_test = []
for i in range(60, len(test_data)):
    x_test.append(test_data[i - 60:i, 0])

x_test = np.array(x_test)

# Send data in batches
batch_size = 120  # 120 days
for i in range(0, len(x_test), batch_size):
    batch = x_test[i:i + batch_size].tolist()  # Convert to list for JSON serialization
    producer.send(topic_name, value=batch)
    print(f"Sent batch {i // batch_size + 1}: {len(batch)} records")
    sleep(20)  # 20 seconds delay