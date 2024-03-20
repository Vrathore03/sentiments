import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

class MoodClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim):
        super(MoodClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.fc1 = nn.Linear(embedding_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)
        out = self.fc1(embedded.view(-1, embedded.size(-1)))
        out = self.relu(out)
        out = self.fc2(out)
        return out

def train_model(model, train_loader, test_loader, epochs=10, lr=0.001):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)


    for epoch in range(epochs):
        model.train()
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
        print(f'Epoch {epoch+1}/{epochs}, Test Loss: {test_loss:.4f}, Test Accuracy: {accuracy:.2f}%')

def save_model(model, filepath):
    torch.save(model.state_dict(), filepath)

def load_model(model_class, filepath, vocab_size, embedding_dim, hidden_dim, output_dim):
    model = model_class(vocab_size, embedding_dim, hidden_dim, output_dim)
    model.load_state_dict(torch.load(filepath))
    return model
