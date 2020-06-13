from textblob_de import TextBlobDE


class Model:
	""" Parent class (Interface ish) of all models """

	def __init__(self, below_negative, above_positive):
		super().__init__()
		self.below_negative = -0.7
		self.above_positive = 0.7
	
	def get_polarity(self, tweet):
		"""Return the polarity of the tweet as float in the range [-1, 1]."""
		raise NotImplemented

	def get_sentiment_label(self, tweet):
		"""Return the label of the tweet ("pos", "neg", or "neutral")."""
		value = self.get_polarity(tweet)
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
		super().__init__(-0.7, 0.7)
		
	def get_polarity(self, text):
		return TextBlobDE(text).sentiment.polarity
	

if __name__ == "__main__":
	# For testing the model
	
	model = TextBlob()
	
	text_pos = "hallo das ist ein ziemlich guter text und ich bin gut drauf"
	text_neg = "Ich hasse diesen Text, fickt euch alle ihr scheiß Arschlöcher"
	text_neu = "Heute ist Sonntag und morgen ist Montag"

	text_hard = "Oh nein, schon wieder zu viel Geld auf meinem Konto"

	print("label = {} ".format(model.get_sentiment_label(text_pos)))
		
	print(TextBlobDE(text_pos))
	print(type(TextBlobDE(text_pos)))
	print(TextBlobDE(text_pos).sentiment)
	print(TextBlobDE(text_neg).sentiment.polarity)
	print(TextBlobDE(text_neu).sentiment.polarity)

	print(TextBlobDE(text_hard).sentiment.polarity)
