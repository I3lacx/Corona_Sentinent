import os
import pickle

from textblob_de import TextBlobDE
import spacy
import numpy as np
from statistics import mean
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.layers import SpatialDropout1D
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences

from spacy_sentiws import spaCySentiWS
from sentiment_models.vader_translated.vaderSentimentmaster.vaderSentiment.vaderSentiment.vaderSentiment \
    import SentimentIntensityAnalyzer
from sentiment_models.vader_with_sentiws.lib_sentiment_sentiws import SentimentIntensityAnalyzerSentiWS
from sentiment_models.preprocess_tweets import replace_all
from sentiment_models.GerVADER.vaderSentimentGER import SentimentIntensityAnalyzer as GerVaderSentimentIntensityAnalyzer


def preprocess_text(text):
    return replace_all(text)


class Model:
    """ Parent class (Interface ish) of all models """

    def __init__(self, below_negative, above_positive, model_name):
        super().__init__()
        self.below_negative = below_negative
        self.above_positive = above_positive
        self.name = model_name

    def get_polarity_without_preprocessing(self, text):
        """Return the polarity of the tweet as float in the range [-1, 1]."""
        raise NotImplemented
    
    def get_polarity(self, text):
        return self.get_polarity_without_preprocessing(preprocess_text(text))
    
    def get_sentiment_label(self, text):
        return self.get_sentiment_label_without_preprocessing(preprocess_text(text))

    def get_sentiment_label_without_preprocessing(self, text):
        """Return the label of the tweet ("pos", "neg", or "neut")."""
        value = self.get_polarity_without_preprocessing(text)
        if value < self.below_negative:
            label = "neg"
        elif value > self.above_positive:
            label = "pos"
        else:
            label = "neut"
        return label


class TextBlob(Model):
    """ Text Blob Model, for easy testing and comparison """

    def __init__(self):
        super().__init__(-0.7, 0.7, "TextBlob")

    def get_polarity_without_preprocessing(self, text):
        return TextBlobDE(text).sentiment.polarity


class SpacySentiWS(Model):
    """Use spacy plugin to get SentiWS score and average them."""

    def __init__(self):
        super().__init__(-0.37, 0.13, "SpacySentiWS")
        self.nlp = spacy.load('de_core_news_sm')
        sentiws = spaCySentiWS(sentiws_path=os.path.join("sentiment_models", "DATA", "SentiWS"))
        self.nlp.add_pipe(sentiws)

    def get_polarity_without_preprocessing(self, text):
        values = [token._.sentiws for token in self.nlp(text) if token._.sentiws is not None]
        if len(values) == 0:
            value = 0
        else:
            value = mean(values)
        # compute polarity-scores
        return value


class VaderSentiWS(Model):
    """Use the translated version of Vader but replace its word-list with the SentiWS-wordlist"""

    def __init__(self):
        super().__init__(-0.1, 0.1, "VaderSentiWS")
        self.analyzer = SentimentIntensityAnalyzerSentiWS()

    def get_polarity_without_preprocessing(self, text):
        return self.analyzer.polarity_scores(text)["compound"]


class Baseline(Model):
    """Only for comparison, labels all texts as neutral."""

    def __init__(self):
        super().__init__(-0.1, 0.1, "Baseline")
        self.analyzer = None

    def get_sentiment_label(self, text):
        return "neut"


class Vader(Model):
    """Use the translated version of Vader but replace its word-list with the SentiWS-wordlist"""

    def __init__(self):
        super().__init__(-0.1, 0.1, "VaderTranslated")
        self.analyzer = SentimentIntensityAnalyzer()

    def get_polarity_without_preprocessing(self, text):
        return self.analyzer.polarity_scores(text)["compound"]


class GerVADER(Model):
    """Use the translated version of Vader with its original but translated wordlist"""

    def __init__(self):
        super().__init__(-0.34, 0.69, "GerVader")
        self.analyzer = GerVaderSentimentIntensityAnalyzer()

    def get_polarity_without_preprocessing(self, text):
        return self.analyzer.polarity_scores(text)["compound"]


class TrainedSentimentModel(Model):
    """Use the sentiment model we trained"""
    def __init__(self, model_path="./sentiment_models/trained_model", model_name="TrainedModel"):
        super().__init__(0, 0, model_name)
        self._load_model(model_path)
        self._load_tokenizer()
        self.label_translation = {0: "neg", 1: "neut", 2: "pos"}

    def _load_model(self, model_path):
        """Load the model from file"""
        self.analyzer = load_model(model_path)

    def get_polarity_without_preprocessing(self, text):
        """Return the polarity of the tweet as float in the range [-1, 1]."""
        return None

    def get_polarity(self, text):
        return None

    def get_sentiment_label(self, text):
        """Return the label of the tweet after preprocessing it ("pos", "neg", or "neut")."""
        return self.get_sentiment_label_without_preprocessing(preprocess_text(text))
    
    def get_sentiment_labels_batch(self, texts):
        """Return the labels of a list of tweets ("pos", "neg", or "neut") after preprocessing them."""
        preprocessed_texts = [preprocess_text(text) for text in texts]
        return self.get_sentiment_labels_without_preprocessing_batch(preprocessed_texts)

    def get_sentiment_label_without_preprocessing(self, text):
        """Return the label of the tweet ("pos", "neg", or "neut")."""
        predicted = self._do_label_prediction([text])
        return self.label_translation[predicted.item()]
    
    def get_sentiment_labels_without_preprocessing_batch(self, texts):
        """Return the labels of a list of tweets ("pos", "neg", or "neut")."""
        predicted = self._do_label_prediction(texts)
        return [self.label_translation[pred.item()] for pred in predicted]

    def get_label_for_clear_cases(self, texts, pos_boundary=0.8, neg_boundary=0.7):
        if not isinstance(texts, list):
            texts = list(texts)
        texts = [preprocess_text(text) for text in texts]
        prob_dists = self.do_prediction(texts)
        labels = []
        for i in range(len(texts)):
            row = [val.item() for val in prob_dists[i]]
            label = "pos" if row[2] > pos_boundary else "neg" if row[0] > neg_boundary else "neut"
            labels.append(label)
        return labels
    
    def do_prediction(self, prediction_input):
        """Encode the input and predict the label(s)"""
        encoded_text = self.tokenizer.texts_to_sequences(prediction_input)
        passed_encoded_text = pad_sequences(encoded_text, maxlen=200)
        prob_dist = self.analyzer.predict(passed_encoded_text)
        return prob_dist

    def _do_label_prediction(self, prediction_input):
        prob_dist = self.do_prediction(prediction_input)
        predicted = self._get_label_from_prob_dist(prob_dist, len(prediction_input) == 1)
        return predicted

    def _load_tokenizer(self):
        """Load the tokenizer from file"""
        with open('sentiment_models/tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)
        self.tokenizer = tokenizer

    def _get_label_from_prob_dist(self, prob_dist, only_one_input):
        if only_one_input:
            predicted = np.argmax(prob_dist)
        else:
            predicted = np.argmax(prob_dist, axis=1)
        return predicted


if __name__ == "__main__":
    # For testing the model

    model = TextBlob()

    text_pos = "hallo das ist ein ziemlich guter text und ich bin gut drauf"
    text_neg = "Ich hasse diesen Text, fickt euch alle ihr scheiß Arschlöcher"
    text_neu = "Heute ist Sonntag und morgen ist Montag"

    text_hard = "Oh nein, schon wieder zu viel Geld auf meinem Konto"

    print("label = {} ".format(model.get_sentiment_label(text_pos)))
    spacy_model = SpacySentiWS()
    print("label = {} ".format(spacy_model.get_sentiment_label(text_neg)))
    print("label = {} ".format(spacy_model.get_polarity(text_neg)))

    trained_model = TrainedSentimentModel()
    print(trained_model.get_sentiment_labels_batch([text_pos, text_neg, text_neu]))

    print(TextBlobDE(text_pos))
    print(type(TextBlobDE(text_pos)))
    print(TextBlobDE(text_pos).sentiment)
    print(TextBlobDE(text_neg).sentiment.polarity)
    print(TextBlobDE(text_neu).sentiment.polarity)

    print(TextBlobDE(text_hard).sentiment.polarity)
