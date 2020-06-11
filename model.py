from textblob_de import TextBlobDE


class Model:
	""" Parent class (Interface ish) of all models """
	
	def get_polarity(self):
		raise NotImplemented
		
		
class TextBlob(Model):
	""" Text Blob Model, for easy testing and comparison """

	def __init__(self):
		super().__init__()
		
	def get_polarity(self, text):
		return TextBlobDE(text).sentiment.polarity
	

if __name__ == "__main__":
	# For testing the model
	
	model = TextBlob()
	
	text_pos = "hallo das ist ein ziemlich guter text und ich bin gut drauf"
	text_neg = "Ich hasse diesen Text, fickt euch alle ihr scheiß Arschlöcher"
	text_neu = "Heute ist Sonntag und morgen ist Montag"

	text_hard = "Oh nein, schon wieder zu viel Geld auf meinem Konto"

	model.get_polarity(text_pos)
		
		
	print(TextBlobDE(text_pos))
	print(type(TextBlobDE(text_pos)))
	print(TextBlobDE(text_pos).sentiment)
	print(TextBlobDE(text_neg).sentiment.polarity)
	print(TextBlobDE(text_neu).sentiment.polarity)

	print(TextBlobDE(text_hard).sentiment.polarity)
