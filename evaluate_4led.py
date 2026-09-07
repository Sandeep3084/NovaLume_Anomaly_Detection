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

print("Loading normal data to fit scaler and calculate threshold...")
normal_sequences = load_json_folder('1A_sensor_2LED_lamp')
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
model.load_state_dict(torch.load('lstm_autoencoder_weights.pth', map_location=DEVICE))
model.eval()

criterion = nn.MSELoss(reduction='none')

def get_reconstruction_errors(tensor_data):
    loader = DataLoader(TensorDataset(tensor_data), batch_size=BATCH_SIZE, shuffle=False)
    errors = []
    with torch.no_grad():
        for batch_x, in loader:
            batch_x = batch_x.to(DEVICE)
            outputs = model(batch_x)
            loss = criterion(outputs, batch_x)
            seq_loss = loss.mean(dim=(1, 2)).cpu().numpy()
            errors.extend(seq_loss)
    return np.array(errors)

val_tensor = torch.tensor(val_normal_scaled, dtype=torch.float32)
val_errors = get_reconstruction_errors(val_tensor)

threshold = np.mean(val_errors) + 3 * np.std(val_errors)
print(f"Validation Mean Error: {np.mean(val_errors):.6f}, Std: {np.std(val_errors):.6f}")
print(f"Calculated Anomaly Threshold: {threshold:.6f}")

print("\nLoading 1A_sensor_4LED_lamp data...")
test_sequences = load_json_folder('1A_sensor_4LED_lamp')
print(f"Test Sequences (JSON): {test_sequences.shape}")

if len(test_sequences) > 0:
    test_sequences_scaled = scale_sequences(test_sequences, scaler, fit=False)
    test_tensor = torch.tensor(test_sequences_scaled, dtype=torch.float32)
    test_errors = get_reconstruction_errors(test_tensor)
    
    test_anomalies = np.sum(test_errors > threshold)
    print(f"Test Anomalies (4LED): {test_anomalies}/{len(test_errors)}")
    print(f"Anomaly Detection Rate: {test_anomalies/len(test_errors)*100:.2f}%")
else:
    print("No data found in 1A_sensor_4LED_lamp folder.")
