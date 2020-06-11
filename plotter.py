import matplotlib.pyplot as plt
import helper


"""
Plotter, with all the plot functions and stuff
Could be an extra Class, idk

"""

class Plotter:

	def __init__(self, config):
		""" configure settings for all graphs here """
		self.config = config
		self.config_txt = helper.config_to_txt(self.config)
		
	def plot_dict(self, my_dict):
		plt.bar(range(len(my_dict)), list(my_dict.values()), tick_label=list(my_dict.keys()), width=0.6)
		plt.title(self.config["plot"]["title"])
		sub_txt = self.config_txt["query"]
		plt.figtext(0.5, 0.01, sub_txt, wrap=True, horizontalalignment='center', fontsize=12)
		plt.show()

	def simple_hist(self, values):
		plt.hist(values)
		plt.title(self.config["plot"]["title"])
		sub_txt = self.config_txt["query"]
		plt.figtext(0.5, 0.01, sub_txt, wrap=True, horizontalalignment='center', fontsize=12)
		plt.show()

