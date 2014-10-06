from django.http import HttpResponse

import pymongo
import json
from pymongo import MongoClient
from django.http import HttpResponse
import math
import time
import re
from bson.son import SON


def index(request):

	return HttpResponse("home, receive angular client")

def test(request):

	s_out = "out<br/><br/>"
	s_query = "*"


	s_out += "raw query: " + s_query

	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump


	mongo_db.aggregate([
		{"$unwind": "$tags"},
		{"$group": {"_id": "$tags", "count": {"$sum": 1}}},
		{"$sort": SON([("count", -1), ("_id", -1)])}
	])


	return HttpResponse(s_out)

def suggest(request):
	s_query = ""

	if request.method == 'GET' and 'query' in request.GET:
		s_query = request.GET['query']

	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump

	json_response_data = {}

	cursor = mongo_db.media_dump.find({"tags.value":{'$regex':'^sc'}}).limit(10)

	
	for r in cursor:
		#json_response_data['files'].append({"id": r['file_id'], "tags": r["tags"], "lat": f_lat, "lon": f_lon})
		json_response_data['files'].append({"id": r['file_id']})


	s_response = json.dumps(json_response_data)

	http_response = HttpResponse(s_response, content_type="application/json")
	http_response['Access-Control-Allow-Origin'] = '*'
	return http_response



def tree(request):
	
	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump
	

	json_response_data = {}
	json_response_data["tree"] = []


	distinct_cursor = mongo_db.files.find()

	sl_added = []


	
	for r in distinct_cursor:

		s_dir = ""

		for t in r["tags"]:
			if t["type"] == "directory.path_folders":
				s_dir = t["value"]
				if s_dir not in sl_added:
					sl_added.append(s_dir)	
					s_thumb = ""

					try:
						s_thumb = r["base_images"][0]["32"]
					except:
						pass			

					json_response_data['tree'].append({"id": r['file_id'], "dir": s_dir, "data_thumb": s_thumb})
					break


	s_response = json.dumps(json_response_data)

	http_response = HttpResponse(s_response, content_type="application/json")
	http_response['Access-Control-Allow-Origin'] = '*'
	return http_response

def search(request):
	time_start = time.time()

	# defaults
	s_query = "*"
	i_page = 1
	s_sort = "datetime"
	b_sort_direction = "asc"
	s_operator = "and"
	i_per_page = 100

	if request.method == 'GET' and 'query' in request.GET:
		s_query = request.GET['query']

	if request.method == 'GET' and 'sort' in request.GET:
		s_sort = request.GET['sort']
		
	if request.method == 'GET' and 'sort_direction' in request.GET:
		b_sort_direction = request.GET['sort_direction']

	if request.method == 'GET' and 'page' in request.GET:
		if request.GET['page'].isdigit():
			i_page = int(request.GET['page'])
		else:
			i_page = 1

	b_sort_direction = b_sort_direction.lower()

	if b_sort_direction == "asc":
		b_sort_direction = pymongo.ASCENDING
	elif b_sort_direction == "desc":
		b_sort_direction = pymongo.DESCENDING
	

	if request.method == 'GET' and 'operator' in request.GET:
		if(request.GET['operator'] == "or"):
			s_operator = "or"


	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump
	

	json_response_data = {}
	json_response_data["files"] = []
	json_response_data["search_info"] = {"operator": s_operator, "page": i_page, "queries": {}}
	json_response_data["results_info"] = {}


	l_queries = []
	c_files = 0
	c_available_pages = 0
	i_search_milliseconds = 0


	for c_index, s_single_query in enumerate(s_query.split(',')):
		json_response_data["search_info"]["queries"].update({c_index: s_single_query.lower()})
		s_type = ""
		s_value = ""
		if not "=" in s_single_query:
			# text query
			l_queries.append({"tags.value": s_single_query.lower()})
		else:
			# type has been specified
			s_type = s_single_query.split('=')[0].lower()
			s_value = s_single_query.split('=')[1].lower()

			if s_type == "map":
				# hack out lat lon vals and add four queries
				fl_values = s_value.split('|')
				if len(fl_values) == 4:
					l_queries.append({"latitude": {"$gt": float(fl_values[0])}})
					
					l_queries.append({"latitude": {"$lt": float(fl_values[1]) }})
					l_queries.append({"longitude": {"$gt": float(fl_values[2]) }})
					l_queries.append({"longitude": {"$lt": float(fl_values[3]) }})
					
			else:
				# add default straight equals query
				l_queries.append({ "$and" : [ { "tags.type": s_type }, { "tags.value": s_value } ] })

	cursor = mongo_db.files.find( { "$"+s_operator: l_queries } ).skip((i_page-1)*i_per_page).limit(i_per_page).sort(s_sort, b_sort_direction)

	distinct_cursor = mongo_db.files.find( { "$"+s_operator: l_queries } )
	#cursor = mongo_db.files.find( { "$"+s_operator: l_queries } )
	# {tags: { $elemMatch: { value: s_query } } } 
	c_files = cursor.count()


	# calculate available pages
	c_available_pages = (c_files / i_per_page)
	if ((c_files % i_per_page) > 0):
		c_available_pages += 1

	
	for r in cursor:
		#json_response_data['files'].append({r['file_id']:{"id": r['file_id'], "tags": r["tags"]}})
		f_lat = 0
		f_lon = 0
		s_thumb = ""

		for t in r["tags"]:
			if t["type"] == "location.latitude":
				f_lat = t["value"]
			if t["type"] == "location.longitude":
				f_lon = t["value"]

		try:
			s_thumb = r["base_images"][1]
		except:
			pass

		json_response_data['files'].append({"id": r['file_id'], "lat": f_lat, "lon": f_lon, "data_thumb": s_thumb, "type": r["type"]})


	time_end = time.time()
	i_search_milliseconds = (time_end - time_start) * 1000
	
	#l_distinct = cursor.distinct("tags", "{'type': 'directory.word'}")
	l_distinct = distinct_cursor.distinct("tags")

	
	l_filter_distinct = []
	c_distinct = 0
	
	for c_index, tag in enumerate(l_distinct):
		if tag["type"] == "filter.value":
			if tag["value"] not in l_filter_distinct:
				l_filter_distinct.append(tag["value"])
				c_distinct += 1

	l_filter_distinct = sorted(l_filter_distinct)
	


	json_response_data["results_info"] = {"count": c_files, "available_pages": c_available_pages, "speed": i_search_milliseconds, "distinct": l_filter_distinct}

	s_response = json.dumps(json_response_data)

	http_response = HttpResponse(s_response, content_type="application/json")
	http_response['Access-Control-Allow-Origin'] = '*'
	return http_response