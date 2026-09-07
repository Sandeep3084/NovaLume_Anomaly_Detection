import os
import glob
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

SEQ_LENGTH = 40
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_json_folder(folder):
    sequences = []
    files = glob.glob(os.path.join(folder, '*.json'))
    for f in files:
        with open(f, 'r') as file:
            data = json.load(file)
            v = np.array(data['v'])
            i = np.array(data['i'])
            combined = np.column_stack((v, i))
            num_seqs = len(combined) // SEQ_LENGTH
            for s in range(num_seqs):
                sequences.append(combined[s*SEQ_LENGTH : (s+1)*SEQ_LENGTH])
    return np.array(sequences)

def load_csv_folder(folder):
    sequences = []
    files = glob.glob(os.path.join(folder, '*.csv'))
    for f in files:
        df = pd.read_csv(f, on_bad_lines='skip', low_memory=False)
        if 'V_v' in df.columns and 'I_a' in df.columns:
            v = pd.to_numeric(df['V_v'], errors='coerce').fillna(0).values
            i = pd.to_numeric(df['I_a'], errors='coerce').fillna(0).values
            combined = np.column_stack((v, i))
            num_seqs = len(combined) // SEQ_LENGTH
            for s in range(num_seqs):
                sequences.append(combined[s*SEQ_LENGTH : (s+1)*SEQ_LENGTH])
    return np.array(sequences)

print("Loading data...")
normal_sequences = load_json_folder('1A_sensor_2LED_lamp')
print(f"Normal Sequences (JSON): {normal_sequences.shape}")

test_sequences = load_csv_folder('test')
print(f"Test Sequences (CSV): {test_sequences.shape}")

train_normal, val_normal = train_test_split(normal_sequences, test_size=0.2, random_state=42)

scaler = StandardScaler()
def scale_sequences(seqs, scaler, fit=False):
    N, L, F = seqs.shape
    flat = seqs.reshape(-1, F)
    if fit:
        scaled_flat = scaler.fit_transform(flat)
    else:
        scaled_flat = scaler.transform(flat)
    return scaled_flat.reshape(N, L, F)

train_normal_scaled = scale_sequences(train_normal, scaler, fit=True)
val_normal_scaled = scale_sequences(val_normal, scaler, fit=False)
if len(test_sequences) > 0:
    test_sequences_scaled = scale_sequences(test_sequences, scaler, fit=False)
else:
    test_sequences_scaled = np.array([])

train_tensor = torch.tensor(train_normal_scaled, dtype=torch.float32)
train_loader = DataLoader(TensorDataset(train_tensor, train_tensor), batch_size=BATCH_SIZE, shuffle=True)

class LSTMAutoencoder(nn.Module):
    def __init__(self, input_dim=2, hidden_dim=64, num_layers=2):
        super(LSTMAutoencoder, self).__init__()
        self.encoder = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, input_dim, num_layers, batch_first=True)
        
    def forward(self, x):
        _, (h, c) = self.encoder(x)
        last_h = h[-1].unsqueeze(1)
        decoder_input = last_h.repeat(1, x.size(1), 1)
        out, _ = self.decoder(decoder_input)
        return out

model = LSTMAutoencoder(input_dim=2).to(DEVICE)
criterion = nn.MSELoss(reduction='none')
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

print("Training...")
train_loss_history = []
for epoch in range(EPOCHS):
    model.train()
    epoch_train_loss = 0
    for batch_x, _ in train_loader:
        batch_x = batch_x.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_x).mean()
        loss.backward()
        optimizer.step()
        epoch_train_loss += loss.item() * batch_x.size(0)
    epoch_train_loss /= len(train_loader.dataset)
    train_loss_history.append(epoch_train_loss)
    print(f"Epoch {epoch+1}/{EPOCHS} | Train Loss: {epoch_train_loss:.6f}")

# Save the weights
weights_path = 'lstm_autoencoder_weights.pth'
torch.save(model.state_dict(), weights_path)
print(f"Model weights saved to {weights_path}")

print("Evaluating...")
model.eval()

def get_reconstruction_errors(tensor_data):
    loader = DataLoader(TensorDataset(tensor_data), batch_size=BATCH_SIZE, shuffle=False)
    errors = []
    with torch.no_grad():
        for batch_x, in loader:
            batch_x = batch_x.to(DEVICE)
            outputs = model(batch_x)
            loss = criterion(outputs, batch_x)
            # MSE per sequence
            seq_loss = loss.mean(dim=(1, 2)).cpu().numpy()
            errors.extend(seq_loss)
    return np.array(errors)

train_errors = get_reconstruction_errors(train_tensor)
val_tensor = torch.tensor(val_normal_scaled, dtype=torch.float32)
val_errors = get_reconstruction_errors(val_tensor)

threshold = np.mean(val_errors) + 3 * np.std(val_errors)
print(f"Validation Mean Error: {np.mean(val_errors):.6f}, Std: {np.std(val_errors):.6f}")
print(f"Calculated Anomaly Threshold: {threshold:.6f}")

train_anomalies = np.sum(train_errors > threshold)
val_anomalies = np.sum(val_errors > threshold)
print(f"Train Anomalies: {train_anomalies}/{len(train_errors)}")
print(f"Val Anomalies: {val_anomalies}/{len(val_errors)}")

if len(test_sequences_scaled) > 0:
    test_tensor = torch.tensor(test_sequences_scaled, dtype=torch.float32)
    test_errors = get_reconstruction_errors(test_tensor)
    test_anomalies = np.sum(test_errors > threshold)
    print(f"Test Anomalies (CSV test folder): {test_anomalies}/{len(test_errors)}")

import matplotlib.pyplot as plt

# Plot 1: Training Loss
plt.figure(figsize=(8, 5))
plt.plot(range(1, EPOCHS + 1), train_loss_history, marker='o', linestyle='-', color='b')
plt.title('Training Loss per Epoch')
plt.xlabel('Epoch')
plt.ylabel('Mean Squared Error (MSE)')
plt.grid(True)
plt.savefig('training_loss.png')
print("Saved training_loss.png")
plt.close()

# Plot 2: Error Distribution
plt.figure(figsize=(10, 6))
plt.hist(train_errors, bins=30, alpha=0.5, color='blue', label='Train (Normal)')
plt.hist(val_errors, bins=30, alpha=0.5, color='green', label='Validation (Normal)')
if len(test_sequences_scaled) > 0:
    plt.hist(test_errors, bins=30, alpha=0.5, color='red', label='Test (Anomalous)')

plt.axvline(threshold, color='black', linestyle='dashed', linewidth=2, label=f'Threshold ({threshold:.2f})')
plt.title('Reconstruction Error Distribution')
plt.xlabel('Reconstruction Error (MSE)')
plt.ylabel('Frequency')
plt.legend()
plt.grid(True)
plt.savefig('error_distribution.png')
print("Saved error_distribution.png")
plt.close()

