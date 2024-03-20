import sys
sys.path.append('src')
from torch.utils.data import Dataset

class MoodDataset(Dataset):
    def __init__(self, data):
        self.data = data
        self.word_to_idx = {word: idx for idx, word in enumerate(set(data['words']), start=1)}
        self.word_to_idx['<unk>'] = 0  # Add the '<unk>' token with index 0
        self.mood_to_idx = {'happiness': 0, 'sadness': 1, 'depression': 2}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        word = self.data.iloc[idx]['words']
        mood = self.data.iloc[idx]['mood']
        return self.word_to_idx.get(word, 0), self.mood_to_idx[mood]
