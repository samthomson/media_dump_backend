
import os, sys
import pymongo

from os import listdir
from pymongo import MongoClient

def get_files(s_base_dir):
	fileList = []

	for root, subFolders, files in os.walk(s_base_dir):
	    for file in files:
			f = os.path.join(root,file)
			fileList.append(f)

	return fileList

if __name__ == '__main__':

	s_seed_dir = '../media'

	# get all files from [media] folder
	sa_files = get_files(s_seed_dir)
	#for s_file in sa_files:
	#	print s_file

	# get all files from db
	client = MongoClient()

	db = client.media_dump

	collection = db.files

var allProductsArray = db.products.find().toArray();

	for o_file in collection.find().toArray():
		print o_file[0]

	# get difference

	# queue jobs if any