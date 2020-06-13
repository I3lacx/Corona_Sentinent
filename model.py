import os

from textblob_de import TextBlobDE
import spacy
from numpy import mean
from spacy_sentiws import spaCySentiWS
from sentiment_models.vader_translated.vaderSentimentmaster.vaderSentiment.vaderSentiment.vaderSentiment \
    import SentimentIntensityAnalyzer
from sentiment_models.vader_with_sentiws.lib_sentiment_sentiws import SentimentIntensityAnalyzerSentiWS
from sentiment_models.preprocess_tweets import replace_all


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
        """Return the label of the tweet ("pos", "neg", or "neutral")."""
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


class Vader(Model):
    """Use the translated version of Vader with its original but translated wordlist"""

    def __init__(self):
        super().__init__(-0.33, 0.46, "Vader")
        self.analyzer = SentimentIntensityAnalyzer()

    def get_polarity_without_preprocessing(self, text):
        return self.analyzer.polarity_scores(text)["compound"]


if __name__ == "__main__":
    # For testing the model

    model = TextBlob()

    text_pos = "hallo das ist ein ziemlich guter text und ich bin gut drauf"
    text_neg = "Ich hasse diesen Text, fickt euch alle ihr scheiß Arschlöcher"
    text_neu = "Heute ist Sonntag und morgen ist Montag"

    text_hard = "Oh nein, schon wieder zu viel Geld auf meinem Konto"

    print("label = {} ".format(model.get_sentiment_label_without_preprocessing(text_pos)))
    spacy_model = SpacySentiWS()
    print("label = {} ".format(spacy_model.get_sentiment_label_without_preprocessing(text_neg)))
    print("label = {} ".format(spacy_model.get_polarity_without_preprocessing(text_neg)))

    print(TextBlobDE(text_pos))
    print(type(TextBlobDE(text_pos)))
    print(TextBlobDE(text_pos).sentiment)
    print(TextBlobDE(text_neg).sentiment.polarity)
    print(TextBlobDE(text_neu).sentiment.polarity)

    print(TextBlobDE(text_hard).sentiment.polarity)
