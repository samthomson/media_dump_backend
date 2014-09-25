import os, sys, time
import sqlite3 as sqlite
#from easy_thumbnails.files import get_thumbnailer

execfile("get_lat_lon_exif_pil.py")

import pymongo
from pymongo import MongoClient

import PIL
from PIL import Image


def process_path(i_id):
	'''
	split file path and tag accordingly
	'''
	s_path = s_path_from_id(i_id)
	s_path_no_ext = os.path.splitext(s_path)[0]

	s_path_folders = s_path_no_ext.rsplit('/',1)[0]
	s_path_filename = s_path_no_ext.rsplit('/',1)[1]

	tag(i_id, "text", "*")

	tag(i_id, "directory.path", s_path)
	tag(i_id, "directory.ext", os.path.splitext(s_path)[1].replace('.',''))

	if(s_path.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG'))):
		tag(i_id, "file.type", "image")

	''' go through folder path
	'''
	for ch_delimiter in ['(', ')', '/', '-', '_', '.', ',']:
		if ch_delimiter in s_path_folders:
			s_path_folders = s_path_folders.replace(ch_delimiter, " ")

	sl_dir_words = s_path_folders.split(' ')
	for s_word in sl_dir_words:
		tag(i_id, "directory.folderword", s_word)
		tag(i_id, "filter.value", s_word)

	''' go through file name
	'''
	for ch_delimiter in ['(', ')', '/', '-', '_', '.', ',']:
		if ch_delimiter in s_path_filename:
			s_path_filename = s_path_filename.replace(ch_delimiter, " ")

	sl_dir_words = s_path_filename.split(' ')
	for s_word in sl_dir_words:
		tag(i_id, "directory.fileword", s_word)

def process_location(i_id):
	s_path = s_seed_dir + s_path_from_id(i_id)

	o_image = Image.open(s_path)
	exif_data = get_exif_data(o_image)
	lat_lon = get_lat_lon(exif_data)
	tag(i_id, "location.latitude", lat_lon[0])
	tag(i_id, "location.longitude", lat_lon[1])




def process_thumbs(i_id):
	print "make thumb for %s" % i_id
	s_path = s_path_from_id(i_id)
	s_source_path = s_seed_dir + s_path_from_id(i_id)

	make_thumb(s_source_path, "../thumb/icon/" + str(i_id) + '.jpg', 32)
	make_thumb(s_source_path, "../thumb/thumb/" + str(i_id) + '.jpg', 300)
	make_thumb(s_source_path, "../thumb/lightbox/" + str(i_id) + '.jpg', 1200)

	"""
	im_temp = Image.open(s_source_path)
	i_shortest_side_of_temp = min(im_temp.size)
	# ensure it's a square
	im_temp = im_temp.crop((0,0,i_shortest_side_of_temp,i_shortest_side_of_temp))
	# make a thumbnail, as per block size
	im_temp.thumbnail((125, 125))
	im_temp.save("../thumb/thumb/" + str(i_id) + '.jpg');
	print "made thumb for %s @ %s" % (i_id,s_path.replace("/","-"))
	"""


def make_thumb(s_in, s_out, i_target_height):
	targetHeight = i_target_height
	img = Image.open(s_in)
	hpercent = (targetHeight/float(img.size[1]))
	wsize = int((float(img.size[0])*float(hpercent)))
	img = img.resize((wsize,targetHeight), PIL.Image.ANTIALIAS)
	img.save(s_out)







def tag(s_file_id, s_tag_type, s_value):
	if s_value != "":
		s_tag_type = s_tag_type.lower()
		if(isinstance(s_value, basestring)):
			s_value = s_value.lower()
			
		#db_cursor.execute('''INSERT INTO tags (file_id, type, value) VALUES (?,?,?)''', (s_file_id, s_tag_type, s_value,))
		item = collection_files.find_one({'file_id': s_file_id});
		if item != None:
			# item already exists, add tag to it
			#tags = item.tags
			#tags.add({"type": s_tag_type, "value": s_value})
			print "update"
			#collection_files.update({'file_id': s_file_id},{'tags': [{"type": s_tag_type, "value": s_value}]})

			collection_files.update({'file_id' : s_file_id}, { '$push':{'tags': {"type": s_tag_type, "value": s_value}}})
		else:
			# create document with tag as property
			print "insert"
			collection_files.insert({'file_id': s_file_id, 'tags': [{"type": s_tag_type, "value": s_value}]})


















def s_path_from_id(i_file_id):
	db_cursor.execute('''SELECT path FROM files WHERE id=?''', (i_file_id,))
	return db_cursor.fetchone()[0]

"""
these should be shared
"""
def queue_file(s_file_id, s_queue, s_datetime_from = time.strftime('%Y-%m-%d %H:%M:%S')):
	db_cursor.execute('''INSERT INTO queue (queue, file_id, datetime_from) VALUES (?,?,?)''', (s_queue, s_file_id, s_datetime_from,))

def dequeue_file(i_id):
	#print "dequeue, off for now"
	db_cursor.execute('''DELETE FROM queue WHERE file_id=?''', (i_id,))

if __name__ == '__main__':

	s_seed_dir = '../media'

	# connect to db
	db = sqlite.connect('media_dump_db')
	db_cursor = db.cursor()

	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump
	# get files collection (table)
	collection_files = mongo_db.files

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

		if s_queue == "make_thumbnails":
			process_thumbs(i_file_id)

		if s_queue == "location":
			process_location(i_file_id)


		# remove it from queue
		dequeue_file(i_file_id)

		# re-queue for lucene
		#queue_file(i_file_id, "lucene.index")

	db.commit()
	db.close()