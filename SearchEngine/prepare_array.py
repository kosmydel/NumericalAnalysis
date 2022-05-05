import glob
import json
import os
import sys

import numpy as np
import scipy
from scipy.sparse import csr_matrix
from tqdm import tqdm
from nltk.stem import PorterStemmer
from sparsesvd import sparsesvd

ps = PorterStemmer()

def make_array(dictionary='dictionary_mini.json', processed_dir='./processed_mini', files_prefix='./data', not_save=False):
	with open(dictionary) as f:
		my_dict = json.load(f)

	m = len(my_dict)

	# Indexes for each work in A matrix
	indexes = {}
	indexes_occurrences = [None] * m
	for i, (word, occ) in enumerate(my_dict.items()):
		indexes[word] = i
		indexes_occurrences[i] = occ

	os.chdir(processed_dir)
	processed_files = glob.glob("*.txt")

	n = len(processed_files)

	A = np.zeros((m, n), dtype=np.single)

	file_names = [None] * len(processed_files)

	i = 0

	for file in tqdm(processed_files):
		file_names[i] = file
		with open(file) as f:
			file_words_occurrences = json.load(f)
			counter = 0
			for word, occurrences in file_words_occurrences.items():
				if word in indexes:
					A[indexes[word]][i] = occurrences
					counter += 1

			if counter > 0:
				i += 1

	# Remove unused files
	A = A[:, : i]

	# IDF
	for j in range(m):
		A[j] *= np.log(i / indexes_occurrences[j])

	print(np.sum(np.linalg.norm(A, axis=0) == 0))

	A_normed = A / np.linalg.norm(A, axis=0)
	A = scipy.sparse.csc_matrix(A_normed)

	print('Saving array to the file...')

	os.chdir('..')

	with open(f"{files_prefix}_indexes.json", 'w') as f:
		json.dump(indexes, f)

	scipy.sparse.save_npz(f"{files_prefix}_matrix.npz", A)

	with open(f"{files_prefix}_filenames.json", 'w') as f:
		json.dump(file_names, f)

	print('Successfully saved!')

	return indexes, A, file_names

def load_data_from_file(files_prefix='./data'):
	with open(f"{files_prefix}_indexes.json") as f:
		indexes = json.load(f)

	A = scipy.sparse.load_npz(f"{files_prefix}_matrix.npz")

	with open(f"{files_prefix}_filenames.json") as f:
		filenames = json.load(f)

	return indexes, A, filenames


def svd_process(A, k=500, filename='./svd_500'):
	ut, s, vt = sparsesvd(A, k)
	res = np.dot(ut.T, np.dot(np.diag(s), vt))
	# np.save(f"{filename}.npy", res)
	return res


def load_matrix_from_file(input_file='./svd_500'):
	return np.load(f'{input_file}.npy')

def query_data(query, indexes, A, file_names, k=5):
	def process_word(x):
		x = x.lower()
		x = ''.join(filter(str.isalpha, x))
		x = ps.stem(x)
		return x

	n = len(indexes)
	file_names = np.array(file_names)

	# Create new vector
	q0 = np.zeros(n, np.int8)
	for word in query.split():
		word = process_word(word)
		if word not in indexes:
			print(f"Couldn't find word {word}...")
			continue
		q0[indexes[word]] = 1

	# Normalize vectors
	q0_normalized = q0 / (np.linalg.norm(q0) + 0.00001)

	# Create correlation vector
	corr_vector = np.abs(q0_normalized @ A)

	# Find items with the highest correlation
	ind = np.argpartition(corr_vector, -k)[-k:]
	ind = ind[np.argsort(corr_vector[ind])][::-1]

	return list(zip(corr_vector[ind], file_names[ind]))


if __name__ == '__main__':
	make_array(
		dictionary="main_dictionary.json",
		processed_dir="./processed_sites",
		files_prefix="./main_data",
	)
	make_array(
		dictionary="mini_dictionary.json",
		processed_dir="./processed_sites_mini",
		files_prefix="./mini_data",
	)

