
import os, sys
import sqlite3 as sqlite

from os import listdir

def get_physical_files(s_base_dir):
	fileList = []

	for root, subFolders, files in os.walk(s_base_dir):
		for file in files:
			f = os.path.join(root,file)
			fileList.append(f)

	return fileList

def get_db_files(db_cursor):
	fileList = []

	db_cursor.execute('''SELECT path FROM files''')

	data=db_cursor.fetchall()
	COLUMN = 0
	column=[elt[COLUMN] for elt in data]

	return fileList

if __name__ == '__main__':

	s_seed_dir = '../media'

	db = sqlite.connect('media_dump_db')
	db_cursor = db.cursor()


	# get all files from [media] folder
	sl_physical_files = get_physical_files(s_seed_dir)
	sl_db_files = get_db_files(db_cursor)

	for s_file in sl_physical_files:
		print "disk: %s" % s_file

	for s_file in sl_db_files:
		print "db: %s" % s_file


	# get difference

	# queue jobs if any