
import numpy as np
import matplotlib.pyplot as plt
import torch
from torch import nn
import QuantLib as ql
from scipy.optimize import differential_evolution
from heston_fft import *








import torch
import torch.nn as nn
import torch.nn.functional as F

class CNNLSTMModel(nn.Module):
    def __init__(self, num_features, num_output_features):
        super(CNNLSTMModel, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=num_features, out_channels=64, kernel_size=3, padding=1)
        self.lstm = nn.LSTM(input_size=64, hidden_size=128, batch_first=True)
        self.dense = nn.Linear(128, num_output_features)

    def forward(self, x):
        # x shape: [batch_size, sequence_length, num_features]
        x = x.permute(0, 2, 1)  # Rearrange to [batch_size, num_features, sequence_length] for Conv1D
        x = F.relu(self.conv1(x))
        x = x.permute(0, 2, 1)  # Rearrange back for LSTM
        x, _ = self.lstm(x)
        x = self.dense(x[:, -1, :])  # Only take the output from the last time step
        return x

    def apply_fft(self, x):
        # Apply FFT on the last layer's outputs (post-processing)
        fft_output = torch.fft.rfft(x)
        return fft_output

def huber_loss_with_fft(y_true, y_pred, delta=1.0):
    fft_true = torch.fft.rfft(y_true)
    fft_pred = torch.fft.rfft(y_pred)
    
    error = torch.abs(fft_true - fft_pred)
    condition = error <= delta
    squared_loss = 0.5 * torch.pow(error, 2)
    linear_loss = delta * (error - 0.5 * delta)
    
    loss = torch.where(condition, squared_loss, linear_loss)
    return torch.mean(loss)
