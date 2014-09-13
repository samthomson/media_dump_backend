import os, sys, time
import sqlite3 as sqlite
#from get_lat_lon_exif_pil import gpsdata
execfile("get_lat_lon_exif_pil.py")
#import get_lat_lon_exif_pil


def process_path(i_id):
	'''
	split file path and tag accordingly
	'''
	s_path = s_path_from_id(i_id)
	s_path_no_ext = os.path.splitext(s_path)[0]

	tag(i_id, "directory.path", s_path)
	tag(i_id, "directory.ext", os.path.splitext(s_path)[1].replace('.',''))
	if(s_path.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG'))):
		tag(i_id, "file.type", "image")

	for ch_delimiter in ['(', ')', '/', '-', '_', '.', ',']:
		if ch_delimiter in s_path_no_ext:
			s_path_no_ext = s_path_no_ext.replace(ch_delimiter, " ")

	sl_dir_words = s_path_no_ext.split(' ')
	for s_word in sl_dir_words:
		tag(i_id, "directory.word", s_word)

def process_location(i_id):

	s_path = s_seed_dir + s_path_from_id(i_id)

	o_image = Image.open(s_path)
	exif_data = get_exif_data(o_image)
	lat_lon = get_lat_lon(exif_data)
	tag(i_id, "location.latitude", lat_lon[0])
	tag(i_id, "location.longitude", lat_lon[1])




def process_thumbs(i_id):
	print "TODO"

def tag(s_file_id, s_tag_type, s_value):
	if s_value != "":
		db_cursor.execute('''INSERT INTO tags (file_id, type, value) VALUES (?,?,?)''', (s_file_id, s_tag_type, s_value,))

def s_path_from_id(i_file_id):
	db_cursor.execute('''SELECT path FROM files WHERE id=?''', (i_file_id,))
	return db_cursor.fetchone()[0]

"""
these should be shared
"""
def queue_file(s_file_id, s_queue, s_datetime_from = time.strftime('%Y-%m-%d %H:%M:%S')):
	db_cursor.execute('''INSERT INTO queue (queue, file_id, datetime_from) VALUES (?,?,?)''', (s_queue, s_file_id, s_datetime_from,))

def dequeue_file(i_id):
	db_cursor.execute('''DELETE FROM queue WHERE file_id=?''', (i_id,))

if __name__ == '__main__':

	s_seed_dir = '../media'

	# connect to db
	db = sqlite.connect('media_dump_db')
	db_cursor = db.cursor()

	# get first item

	db_cursor.execute('''SELECT * FROM queue WHERE active=0 AND datetime_from < ?''',(time.strftime('%Y-%m-%d %H:%M:%S'),))
	o_files = db_cursor.fetchall()
	
	for o_item in o_files:
		#print "process %s" % o_item
		i_id = o_item[0]
		s_queue = o_item[1]
		i_file_id = o_item[2]

		# pass it to relevant processor function
		if s_queue == "path":
			process_path(i_file_id)

		if s_queue == "thumbnails":
			process_thumbs(i_file_id)

		if s_queue == "location":
			process_location(i_file_id)


		# remove it from queue
		dequeue_file(i_file_id)

		# re-queue for lucene
		queue_file(i_file_id, "lucene.index")

	db.commit()
	db.close()
