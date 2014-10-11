import os, sys, time
import sqlite3 as sqlite

from os import listdir

import hashlib

execfile("queue.py")

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

def process_new_file(s_path):
	'''
	add to db, queue accordingly
	'''
	# add to files table
	s_file_id = hashlib.sha1(s_path).hexdigest()
	db_cursor.execute('''INSERT OR IGNORE INTO files (id, path) VALUES (?, ?)''', (s_file_id, s_path,))

	# queue

	# default queue
	if(s_path.lower().endswith(('.jpg', '.jpeg', '.avi', '.mp4', '.mov'))):
		queue_file(s_file_id, "path")


	# pictures
	if(s_path.lower().endswith(('.jpg', '.jpeg'))):
		queue_file(s_file_id, "colour")
		queue_file(s_file_id, "exif_geo")
		queue_file(s_file_id, "places")
		queue_file(s_file_id, "elevation")
		queue_file(s_file_id, "date_taken")
		queue_file(s_file_id, "make_thumbnails")
		#queue_file(s_file_id, "detect_faces")

	# videos
	if(s_path.lower().endswith(('.avi', '.mp4'))):
		queue_file(s_file_id, "video")

	


def process_dead_file(s_path):
	# get id
	db_cursor.execute('''SELECT id FROM files WHERE path=?''', (s_path,))

	i_file_id = db_cursor.fetchone()[0]

	# remove from files table


	db_cursor.execute('''DELETE FROM files WHERE path=?''', (s_path,))
	s_file_id = db_cursor.lastrowid

	# remove from any queues
	#print "delete ID: %s" % i_file_id
	db_cursor.execute('''DELETE FROM queue WHERE file_id=?''', (i_file_id,))
	# remove tags
	# TODO
	# schedule to be removed from lucene index
	# TODO
	# schedule thumbnails to be deleted
	# TODO


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
			#print "new file on disk: %s" % s_physical_file
			process_new_file(s_physical_file)
			i_found_files = i_found_files + 1

	print "\n"

	for s_db_file in sl_db_files:
		if s_db_file not in sl_physical_files:
			#print "db file not on disk: %s" % s_db_file
			process_dead_file(s_db_file)
			i_deleted_files = i_deleted_files + 1


	if i_found_files > 0:
		db_cursor.execute('''INSERT INTO log (system,action,value, datetime) VALUES ("crawler", "new files", ?, datetime())''', (i_found_files,))

	if i_deleted_files > 0:
		db_cursor.execute('''INSERT INTO log (system,action,value, datetime) VALUES ("crawler", "lost files", ?, datetime())''', (i_deleted_files,))


	# get difference

	# queue jobs if any

	db.commit()
	db.close()