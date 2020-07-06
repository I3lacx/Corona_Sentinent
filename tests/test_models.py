import unittest
from model import SpacySentiWS, TextBlob, VaderSentiWS, Vader, TrainedSentimentModel, GerVADER


class TestModels(unittest.TestCase):
    def setUp(self):
        self.model_list = [GerVADER, SpacySentiWS, TextBlob, VaderSentiWS, Vader, TrainedSentimentModel]
        text_pos = "hallo das ist ein ziemlich guter text und ich bin gut drauf :)"
        text_neg = "Ich hasse diesen Text, fickt euch alle ihr scheiß Arschlöcher :("
        text_neu = "Heute ist Sonntag und morgen ist Montag"
        self.tweets = [("pos", text_pos), ("neg", text_neg), ("neut", text_neu)]

    def test_output(self):
        for model in self.model_list:
            current_model = model()
            if current_model.name == "TrainedModel":
                tweet_texts = [tweet_text for label, tweet_text in self.tweets]
                tweet_labels = [label for label, tweet_text in self.tweets]
                guessed_labels = current_model.get_sentiment_labels_batch(tweet_texts)
                self.assertEqual(tweet_labels[:1], guessed_labels[:1])
            for real_label, text in self.tweets:
                try:
                    guessed_label = current_model.get_sentiment_label(text)
                    self.assertIsInstance(guessed_label, str)
                    if not current_model.name == "TrainedModel":
                        guessed_polarity = current_model.get_polarity(text)
                        self.assertTrue(isinstance(guessed_polarity, float) or isinstance(guessed_polarity, int))
                except Exception as e:
                    e.args += ("occured while testing the {} model".format(current_model.name))
                    raise
                try:
                    self.assertEqual(guessed_label, real_label)
                except AssertionError as e:
                    print("model {} did guess label {} for the {} text.".format(current_model.name, guessed_label,
                                                                                real_label))
                try:
                    if not (real_label == "neut" and current_model.name == "TrainedModel"):
                        self.assertNotEqual(guessed_polarity, current_model.get_sentiment_label(text[:-2]))
                except AssertionError as e:
                    print("model {} did not change polarity when {} smiley was removed.".format(current_model.name,
                                                                                                real_label))


if __name__ == "__main__":
    unittest.main()
