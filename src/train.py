import sys
sys.path.append('src')

import pandas as pd
import torch
from torch.utils.data import DataLoader
from datasets import MoodDataset
from models import MoodClassifier, train_model, save_model
from utils import setup_logging, log_exception

def main(data, epochs=100, batch_size=32, lr=0.001, embedding_dim=100, hidden_dim=128):
    # Load the dataset
    dataset = MoodDataset(data)
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Instantiate the model
    vocab_size = len(dataset.word_to_idx)
    output_dim = len(dataset.mood_to_idx)
    model = MoodClassifier(vocab_size, embedding_dim, hidden_dim, output_dim)

    # Train the model
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        for words, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(words)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    # Evaluate the model
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for words, labels in test_loader:
            outputs = model(words)
            test_loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)
            correct += (predicted == labels).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100 * correct / len(test_loader.dataset)
    print(f'Test Loss: {test_loss:.4f}, Test Accuracy: {accuracy:.2f}%')

    # Save model
    save_model(model, 'models/mood_classifier.pth')

if __name__ == '__main__':
    try:
        data = pd.read_csv('dataset/hinglish_emotion_dataset.csv')
        main(data=data)
    except Exception as e:
        log_exception(e)
