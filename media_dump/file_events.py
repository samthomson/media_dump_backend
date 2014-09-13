import os, sys
import sqlite3 as sqlite

from os import listdir

def get_physical_files(s_base_dir):
	fileList = []

	for root, subFolders, files in os.walk(s_base_dir):
		for file in files:
			f = os.path.join(root,file)
			fileList.append(f.replace(s_base_dir, ""))

	return fileList

def get_db_files(db_cursor):
	db_cursor.execute('''SELECT path FROM files''')

	data=db_cursor.fetchall()
	COLUMN = 0
	fileList=[elt[COLUMN] for elt in data]

	return fileList

def process_new_file(s_path, db_cursor):
	# add to db, queue accordingly
	db_cursor.execute('''INSERT OR IGNORE INTO files (path) VALUES (?)''', (s_path,))


def process_dead_file(s_path, db_cursor):
	print "delete from system: %s" % s_path
	# remove from files table
	db_cursor.execute('''DELETE FROM files WHERE path=?''', (s_path,))

	# remove from any queues

	# remove tags

	# schedule to be removed from lucene index

	# schedule thumbnails to be deleted



if __name__ == '__main__':

	s_seed_dir = '../media'

	db = sqlite.connect('media_dump_db')
	db_cursor = db.cursor()

	i_found_files = 0
	i_deleted_files = 0


	# get all files from [media] folder
	sl_physical_files = get_physical_files(s_seed_dir)
	sl_db_files = get_db_files(db_cursor)


	print "\n"
	print "%i files in db" % len(sl_db_files)
	print "%i files on disk\n" % len(sl_physical_files)

	for s_physical_file in sl_physical_files:
		if s_physical_file not in sl_db_files:			
			print "new file on disk: %s" % s_physical_file
			process_new_file(s_physical_file, db_cursor)
			i_found_files = i_found_files + 1

	print "\n"

	for s_db_file in sl_db_files:
		if s_db_file not in sl_physical_files:
			print "db file not on disk: %s" % s_db_file
			process_dead_file(s_db_file, db_cursor)
			i_deleted_files = i_deleted_files + 1


	if i_found_files > 0:
		db_cursor.execute('''INSERT INTO log (system,action,value, datetime) VALUES ("crawler", "new files", ?, datetime())''', (i_found_files,))

	if i_deleted_files > 0:
		db_cursor.execute('''INSERT INTO log (system,action,value, datetime) VALUES ("crawler", "lost files", ?, datetime())''', (i_deleted_files,))


	# get difference

	# queue jobs if any

	db.commit()
	db.close()