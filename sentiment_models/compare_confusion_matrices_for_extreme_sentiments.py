from model import Vader, VaderSentiWS, TextBlob, SpacySentiWS, GerVADER, TrainedSentimentModel, Baseline
from sentiment_models.train_test_dev_split_european_corpus import read_data
from sklearn.metrics import classification_report, confusion_matrix

INPUT_PATH = "sentiment_models/DATA/European_twitter_sentiment_german/German_Twitter_sentiment_test_preprocessed.csv"

models = [GerVADER(), SpacySentiWS(), TextBlob(), VaderSentiWS(), Vader(),
		  TrainedSentimentModel(model_name="LSTM emb. trainable"),
		  TrainedSentimentModel(model_path="./sentiment_models/trained_lstm_embeddings_untrainable",
								model_name="LSTM emb. untrainable"),
		  TrainedSentimentModel(model_path="./sentiment_models/trained_bilstm_model",
								model_name="BiLSTM emb. trainable")]


if __name__ == "__main__":
	input_data = read_data(INPUT_PATH)
	true_labels = [tweet["label"] for tweet in input_data]
	for current_model in models:
		currently_predicted_labels = current_model.get_label_for_clear_cases([tweet["text"] for tweet in input_data])
		# [current_model.get_sentiment_label(tweet["text"]) for tweet in input_data]
		print("\nModel {}:".format(current_model.name))
		print(classification_report(true_labels, currently_predicted_labels))
		conf_matrix = confusion_matrix(true_labels, currently_predicted_labels)
		sums = ["sums"]
		for i in range(3):
			current_sum = sum([conf_matrix[j][i] for j in range(len(conf_matrix))])
			sums.append(current_sum)
		conf_matrix_string = " \\\\\n & ".join(
			[" & ".join([str(i) for i in inner_list] + [str(sum(inner_list))]) for inner_list in conf_matrix])
		conf_matrix_string += " \\\\\n " + " & ".join([str(i) for i in sums])
		print(" & neg & neut & pos & sum \\\\ \n " + conf_matrix_string)