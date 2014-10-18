import os, sys, time, re
import sqlite3 as sqlite
#from easy_thumbnails.files import get_thumbnailer

execfile("get_lat_lon_exif_pil.py")

import pymongo
from pymongo import MongoClient

import PIL
from PIL import Image
import cStringIO
import base64
import json
import urllib2
import requests
import math

execfile("queue.py")

from datetime import date, timedelta
import subprocess

#import cv2
import glob


def process_faces(i_id):
	s_path = s_seed_dir + s_path_from_id(i_id)

	imagePath = s_path

	b_has_face = False
	b_has_body = False

	# Read the image
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	#
	# look for faces
	#
	for haar in glob.glob("haar/face/*.*"):
		# Create the haar cascade
		faceCascade = cv2.CascadeClassifier(haar)

		# Detect faces in the image
		faces = faceCascade.detectMultiScale(
			gray,
			scaleFactor=1.4,
			minNeighbors=5,
			minSize=(100, 100)
		)

		if len(faces) > 0:
			if b_has_face == False:
				b_has_face = True

	#
	# look for bodies
	#
	for haar in glob.glob("haar/faces/*.*"):	
		# Create the haar cascade
		faceCascade = cv2.CascadeClassifier(haar)

		# Detect faces in the image
		faces = faceCascade.detectMultiScale(
			gray,
			scaleFactor=1.4,
			minNeighbors=5,
			minSize=(100, 100)
		)

		if len(faces) > 0:
			if b_has_body == False:
				b_has_body = True

	set_on_document(i_id, "face", b_has_face)
	set_on_document(i_id, "body", b_has_body)

	tag(i_id, "face", b_has_face)
	tag(i_id, "body", b_has_body)


def process_path(i_id):
	'''
	split file path and tag accordingly
	'''
	s_path = s_path_from_id(i_id).lower()
	print "process path: %s" % s_path
	s_path_no_ext = os.path.splitext(s_path)[0]

	s_path_folders = s_path_no_ext.rsplit('/',1)[0]
	s_path_filename = s_path_no_ext.rsplit('/',1)[1]
	s_extension = os.path.splitext(s_path)[1].replace('.','')

	tag(i_id, "text", "*")

	tag(i_id, "directory.path", s_path)
	tag(i_id, "directory.path_folders", s_path_folders)
	tag(i_id, "directory.ext", s_extension)

	if s_extension == "jpg" or s_extension == "jpeg":
		set_on_document(i_id, "type", "image")

	if s_extension == "avi" or s_extension == "mp4":
		set_on_document(i_id, "type", "video")

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


def process_exif_geo(i_id):
	# get the lat lon tags and save as tags
	s_path = s_seed_dir + s_path_from_id(i_id)

	o_image = Image.open(s_path)
	exif_data = get_exif_data(o_image)
	lat_lon = get_lat_lon(exif_data)
	tag(i_id, "location.latitude", lat_lon[0])
	tag(i_id, "location.longitude", lat_lon[1])
	tag(i_id, "date.datetime", exif_data["DateTime"])

	set_on_document(i_id, "latitude", lat_lon[0])
	set_on_document(i_id, "longitude", lat_lon[1])
	set_on_document(i_id, "datetime", exif_data["DateTime"])

def process_places(i_id):
	# get the lat lon tags and get place tags from google
	s_path = s_seed_dir + s_path_from_id(i_id)

	o_image = Image.open(s_path)
	exif_data = get_exif_data(o_image)
	lat_lon = get_lat_lon(exif_data)


	if(lat_lon[0] != None and lat_lon[1] != None):
		# get place tags from google
		s_req_string = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(lat_lon[0])+","+str(lat_lon[1])

		r = requests.get(s_req_string)
		data = r.json()

		if data["status"] == "OK":
			for item in data["results"][0]["address_components"]:
				tag(i_id, "location.place", item["long_name"])
				b_filter_tag = False
				# types which a filter tag will be added for
				#if "route" in item["types"]:
				#	b_filter_tag = True
				if "country" in item["types"]:
					b_filter_tag = True
				if "locality" in item["types"]:
					b_filter_tag = True
				if "administrative_area_level_2" in item["types"]:
					b_filter_tag = True
				#if "postal_code" in item["types"]:
				#	b_filter_tag = True

				if b_filter_tag:
					tag(i_id, "filter.value", item["long_name"])

			tag(i_id, "location.address", data['results'][0]['formatted_address'])
			set_on_document(i_id, "address", data['results'][0]['formatted_address'])

		elif data["status"] == "OVER_QUERY_LIMIT":
			# requeue plus 24 hours
			queue_file(i_id, "places", str(date.today() + timedelta(days=1)))

def process_elevation(i_id):
	# get lat lon and query google for elevation
	s_path = s_seed_dir + s_path_from_id(i_id)

	o_image = Image.open(s_path)
	exif_data = get_exif_data(o_image)
	lat_lon = get_lat_lon(exif_data)

	
	if(lat_lon[0] != None and lat_lon[1] != None):
		# get place tags from google
		s_req_string = "http://maps.googleapis.com/maps/api/elevation/json?locations="+str(lat_lon[0])+","+str(lat_lon[1])

		r = requests.get(s_req_string)
		data = r.json()

		if data["status"] == "OK":
			tag(i_id, "location.elevation", data['results'][0]['elevation'])
			set_on_document(i_id, "elevation", data['results'][0]['elevation'])
			# set on document too

		elif data["status"] == "OVER_QUERY_LIMIT":
			# requeue plus 24 hours
			queue_file(i_id, "elevation", str(date.today() + timedelta(days=1)))

def get_colors(infile, outfile = '', numcolors=1, swatchsize=20, resize=150):
 
	image = Image.open(infile)
	image = image.resize((resize, resize))
	result = image.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
	result.putalpha(0)
	colors = result.getcolors(resize*resize)

	return colors[0][1]

def process_colour(i_id):
	# get lat lon and query google for elevation
	s_path = s_seed_dir + s_path_from_id(i_id)

	t_colours = get_colors(s_path)

	# get average colour and store r g b and rgb colour
	set_on_document(i_id, "red", t_colours[0])
	set_on_document(i_id, "green", t_colours[1])
	set_on_document(i_id, "blue", t_colours[2])


def process_video(s_id):
	# get lat lon and query google for elevation
	s_path = s_seed_dir + s_path_from_id(s_id)

	#
	# convert to relevant formats
	#

	# mp4
	subprocess.call('ffmpeg -i "'+s_path+'" -b 900k -vcodec libx264 -g 30 -strict -2 "../thumb/video/'+s_id+'.mp4" -acodec aac', shell=True)

	# ogv 
	subprocess.call('ffmpeg -i "'+s_path+'" -acodec libvorbis -ac 2 -ab 96k -ar 44100 -r 15 -b 900k "../thumb/video/'+s_id+'.ogv"', shell=True)

	# webm
	subprocess.call('ffmpeg -i "'+s_path+'" -b 345k -vcodec libvpx -acodec libvorbis -ab 160000 -f webm -r 15 -g 40 "../thumb/video/'+s_id+'.webm"', shell=True)

	# create stills for gif and thumb
	i_gif_width = Math.floor(i_thumb_height * 1.5)
	subprocess.call('ffmpeg -ss 00:00:00.000 -i "'+s_path+'" -s '+str(i_gif_width)+':'+str(i_thumb_height)+' -t 00:00:30.000 -vf fps=fps=1/5 -vcodec mjpeg -qscale 10 "../thumb/video/output'+s_id+'_%05d.jpeg"', shell=True)
	
	# create tiny icon
	make_thumb("../thumb/video/output"+s_id+"_00001.jpeg", "db", 32, s_id)

	s_gif_path = "../thumb/video/output"+s_id+".gif"
	
	subprocess.call('convert -delay 60 -layers Optimize "../thumb/video/output'+s_id+'_[0-9]*.jpeg" '+s_gif_path, shell=True)

	purge("../thumb/video", 'output'+s_id+'_[0-9]*.jpeg')

	# save a base 64 image to db
	contents = base64.encodestring(open(s_gif_path,"rb").read())


	os.remove(s_gif_path)
	
	# insert or update
	item = collection_files.find_one({'file_id': s_id});

	if item != None:
		# item already exists, add tag to it
		collection_files.update({'file_id' : s_id}, { '$push':{'base_images': {str(i_thumb_height): contents}}})
	else:
		# create document with tag as property
		collection_files.insert({'file_id' : s_id, 'base_images': [{str(i_thumb_height): contents}]})
		
	

	# create first frame for lightbox load
	
	
def purge(dir, pattern):
    for f in os.listdir(dir):
    	if re.search(pattern, f):
    		os.remove(os.path.join(dir, f))

def process_thumbs(s_id):
	s_path = s_path_from_id(s_id)
	s_source_path = s_seed_dir + s_path_from_id(s_id)

	make_thumb(s_source_path, "db", 32, s_id)
	make_thumb(s_source_path, "db", i_thumb_height, s_id)
	make_thumb(s_source_path, "../thumb/thumb/" + s_id + '.jpg', i_thumb_height)
	make_thumb(s_source_path, "../thumb/lightbox/" + s_id + '.jpg', 1200)


def make_thumb(s_in, s_out, i_target_height, s_file_id = None):
	targetHeight = i_target_height
	img = Image.open(s_in)
	hpercent = (targetHeight/float(img.size[1]))
	wsize = int((float(img.size[0])*float(hpercent)))
	img = img.resize((wsize,targetHeight), PIL.Image.ANTIALIAS)
	if s_out != 'db':
		# save a physical file
		img.save(s_out)
	else:
		# save a base 64 image to db
		output = cStringIO.StringIO()
		s_format = "JPEG"

		img.save(output, s_format)
		contents = output.getvalue()
		contents = base64.standard_b64encode(output.getvalue())
		output.close()
		
		# insert or update
		item = collection_files.find_one({'file_id': s_file_id});

		if item != None:
			# item already exists, add tag to it
			collection_files.update({'file_id' : s_file_id}, { '$push':{'base_images': {str(i_target_height): contents}}})
		else:
			# create document with tag as property
			collection_files.insert({'file_id' : s_file_id, 'base_images': [{str(i_target_height): contents}]})
		







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
			collection_files.update({'file_id' : s_file_id}, { '$push':{'tags': {"type": s_tag_type, "value": s_value}}})
		else:
			# create document with tag as property
			collection_files.insert({'file_id': s_file_id, 'tags': [{"type": s_tag_type, "value": s_value}]})
		
def set_on_document(i_document_id, s_property_name, s_value, b_unique = True):
	#
	collection_files.update({'file_id' : i_document_id}, {'$set': {s_property_name: s_value}}, b_unique)




def s_path_from_id(s_file_id):
	db_cursor.execute('''SELECT path FROM files WHERE id=?''', (s_file_id,))
	return db_cursor.fetchone()[0]

"""
these should be shared
"""
def queue_file(s_file_id, s_queue, s_datetime_from = time.strftime('%Y-%m-%d %H:%M:%S')):
	db_cursor.execute('''INSERT INTO queue (queue, file_id, datetime_from) VALUES (?,?,?)''', (s_queue, s_file_id, s_datetime_from,))

def start_processing(i_item_id):
	# set active value on item in db, so it doesn't get pulled out by anyone else
	db_cursor.execute('''UPDATE queue SET active=1 WHERE id=?''', (i_item_id,))

def dequeue_file(i_id):
	#print "dequeue, off for now"
	db_cursor.execute('''DELETE FROM queue WHERE id=?''', (i_id,))
	db.commit()

if __name__ == '__main__':

	s_seed_dir = '../media'
	s_google_api_key = "AIzaSyBm4wSixAQ7c_gbXczbTeIgoOT7l2xPa5E"
	i_thumb_height = 180

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

		print "item id: %s, file id: %s" % (i_id, i_file_id)

		try:

			# pass it to relevant processor function
			if s_queue == "path":
				start_processing(i_id)
				process_path(i_file_id)

			if s_queue == "make_thumbnails":
				start_processing(i_id)
				process_thumbs(i_file_id)

			if s_queue == "exif_geo":
				start_processing(i_id)
				process_exif_geo(i_file_id)

			if s_queue == "places":
				start_processing(i_id)
				process_places(i_file_id)

			if s_queue == "elevation":
				start_processing(i_id)
				process_elevation(i_file_id)

			if s_queue == "colour":
				start_processing(i_id)
				process_colour(i_file_id)

			if s_queue == "video":
				start_processing(i_id)
				process_video(i_file_id)

			if s_queue == "detect_faces":
				start_processing(i_id)
				process_faces(i_file_id)

		except (RuntimeError, TypeError, NameError):
			print "error processing queue; runtime error: %s, type error: %s, name error: %s" % (RuntimeError, TypeError, NameError)
			set_on_document(i_file_id, "queue processing error", s_queue)
			set_on_document(i_file_id, "error", True)

		# remove it from queue
		dequeue_file(i_id)
		
	db.commit()
	db.close()