import glob
import json
import os
import string
from collections import defaultdict
from tqdm import tqdm
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

ps = PorterStemmer()


def process_files(output: str = "dictionary_mini.json",
				  processed_output: str = "./processed_mini/",
				  directory: str = "./wikiv2",
				  cut_top: float = 0.01,
				  cut_bottom: float = 0.6,
				  min_occurrences = 2,
				  files_to_process=1000):
	"""
	Process crawled files
	cut_top -- top 0.05 of words are removed from dict,
	cut_bottom -- 1 - 0.8 bottom words are removed.

	Function processes '.txt' files from given folder directory.
	Then it clears dictionary by removing all words with less than min_occurrences.
	After that it removes from top cut_top and bottom cut_bottom records (float between 0-1).
	Finally, it saves word occurrences for each file in processed_output folder.
	"""
	def proces_word(x):
		def filt(x1):
			return str.isalpha(x1) or x1 == '-'

		x = x.lower()
		x = ''.join(filter(filt, x))
		x = ps.stem(x)
		return x

	words_occurrences = defaultdict(int)
	stop_words = set(stopwords.words('english'))
	os.chdir(directory)

	for file in tqdm(glob.glob("*.txt")[:files_to_process]):
		file_words = defaultdict(int)
		with open(file, encoding='utf-8') as f:
			for line in f.readlines():
				for word in list(map(proces_word, line.split())):
					if word not in stop_words:
						file_words[word] += 1

		with open('.' + processed_output + file, 'w', encoding='utf-8') as f:
			json.dump(file_words, f)

		for word in file_words.keys():
			words_occurrences[word] += 1

	total_words = len(words_occurrences)
	print('Total words\t', total_words)

	reduced_words1 = {k: v for k, v in words_occurrences.items() if v >= min_occurrences}
	print(f'Removing word with less than {min_occurrences} occurrences...\t', len(reduced_words1))

	reduced_words2 = dict(sorted(reduced_words1.items())[int(len(reduced_words1) * cut_top):int(len(reduced_words1) * cut_bottom)])
	print(f'Reducing size...:\t', len(reduced_words2))

	print(f'Saving results to file {output}')
	os.chdir('..')

	with open(output, 'w', encoding='utf-8') as f:
		json.dump(reduced_words2, f)


if __name__ == '__main__':
	process_files(output="main_dictionary.json",
				  processed_output="./processed_sites/",
				  directory="./wiki",
				  cut_top=0.01,
				  cut_bottom=0.9,
				  min_occurrences=2,
				  files_to_process=25000)

	process_files(output="mini_dictionary.json",
				  processed_output="./processed_sites_mini/",
				  directory="./wiki",
				  cut_top=0.01,
				  cut_bottom=0.6,
				  min_occurrences=2,
				  files_to_process=5000)
