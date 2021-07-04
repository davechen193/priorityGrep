import os
import pprint
import re
from collections import Counter
from subprocess import PIPE, run
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', type=str)
parser.add_argument('--keyTok', type=str)
parser.add_argument('--grepKey', type=str)
parser.add_argument('--depth', type=int)
args = parser.parse_args()

path = args.path; depth = args.depth; keyTok = args.keyTok; grep_key = args.grepKey

def recursive_check_dirs(path, depth, item_only=True):
	check_dirs = []
	if depth == 0:
		return check_dirs
	for item in os.listdir(path):
	    path_item = os.path.join(path, item)
	    if os.path.isfile(path_item) and os.access(path_item, os.R_OK):
	        check_dirs += ([item] if item_only else [path_item])
	    elif os.path.isdir(path_item) and os.access(path_item, os.R_OK):
	        check_dirs += recursive_check_dirs(path_item, depth-1, item_only=item_only)
	    else:
	        "Unknown!"
	return check_dirs

directories = recursive_check_dirs(path, depth)
dirs_subdirs = list(map(lambda dir: (' '.join(list(map(lambda s: '_'.join(s.lower().split()),dir.split('/'))))).lstrip().rstrip(), directories))
dirs_alphanum = list(map(lambda dir: re.sub('[\W_]', ' ', dir), dirs_subdirs))
tokens = list(set((' '.join(dirs_alphanum)).split()))
token2tokens = {}
for dir_str in dirs_alphanum:
	dir_tokens = set(dir_str.split())
	for tok in dir_tokens:
		temp = dir_tokens.copy()
		temp.discard(tok)
		if tok not in token2tokens:
			
			token2tokens[tok] = list(temp)
		else:
			token2tokens[tok] += list(temp)

token2tokenCounts = {}
token2similarTokens = {}
for tok in token2tokens:
	token2tokenCounts[tok] = dict(Counter(token2tokens[tok]))
	total = sum(token2tokenCounts[tok].values(), 0.0)
	token2tokenCounts[tok] = {k: v / total for k, v in token2tokenCounts[tok].items()}
	token2similarTokens[tok] = list(map(lambda tup: tup[1], sorted(list(map(lambda tup: (tup[1], tup[0]), token2tokenCounts[tok].items())))[::-1]))
similarTokens = token2similarTokens[keyTok]

directories_full = list(set(recursive_check_dirs(path, depth, item_only=False)))
dirs = []
for tok in [keyTok] + similarTokens:
	for dir in directories_full:
		if tok in dir:
			dirs.append(dir)
dir_files = []
for dir in dirs:
	if os.path.isfile(dir):
		dir_files.append(dir)

from subprocess import PIPE, run

def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

outputs = []
for i in tqdm(range(0,len(dir_files), 300)):
	output = out("timeout 20s grep " + grep_key + " " + " ".join(dir_files[i:min(i+100, len(dir_files))]))
	outputs.append(output)
for grep_output in filter(None, outputs):
	print(grep_output)