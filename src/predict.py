import sys
sys.path.append('src')

import torch
import pandas as pd
from datasets import MoodDataset
from models import MoodClassifier, load_model
from utils import setup_logging, log_exception


def predict_moods(model, dataset, word_lists):
  try:
        mood_to_label = {0: 'happiness', 1: 'sadness', 2: 'depression'}

        print('\n -------- word_lists --------- \n' , word_lists)
        for words in word_lists:
            word_indices = [dataset.word_to_idx.get(word, 0) for word in words]
            inputs = torch.LongTensor(word_indices)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)

            predicted_moods = [mood_to_label[prediction.item()] for prediction in predicted]

            mood_counts = {
                'happiness': predicted_moods.count('happiness'),
                'sadness': predicted_moods.count('sadness'),
                'depression': predicted_moods.count('depression')
            }

            average_mood = max(mood_counts, key=mood_counts.get)
            print(f"\nAverage Predicted Mood: {average_mood}")
            return average_mood
  except Exception as e:
            log_exception(e)