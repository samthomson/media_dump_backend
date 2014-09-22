from django.http import HttpResponse

import pymongo
import json
from pymongo import MongoClient
from django.http import HttpResponse
import math
import time


def index(request):

	return HttpResponse("home, receive angular client")

def test(request):

	s_out = "out<br/><br/>"
	s_query = "*"

	if request.GET['query'] != None:
		s_query = request.GET['query']


	s_out += "raw query: " + s_query

	#json_query = json.loads(s_query)

	for s_query in s_query.split(','):
		s_out += "<br/>"
		s_out += s_query



	return HttpResponse(s_out)

def search(request):
	time_start = time.time()

	# defaults
	s_query = "*"
	i_page = 1
	s_operator = "and"
	i_per_page = 100

	if request.method == 'GET' and 'query' in request.GET:
		s_query = request.GET['query']

	if request.method == 'GET' and 'page' in request.GET:
		if request.GET['page'].isdigit():
			i_page = int(request.GET['page'])
		else:
			i_page = 1

		

	if request.method == 'GET' and 'operator' in request.GET:
		if(request.GET['operator'] == "or"):
			s_operator = "or"


	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump
	

	json_response_data = {}
	json_response_data["files"] = {}
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

			l_queries.append({ "$and" : [ { "tags.type": s_type }, { "tags.value": s_value } ] })

	cursor = mongo_db.files.find( { "$"+s_operator: l_queries } ).skip((i_page-1)*i_per_page).limit(i_per_page)
	# {tags: { $elemMatch: { value: s_query } } } 
	c_files = cursor.count()


	# calculate available pages
	c_available_pages = (c_files / i_per_page)
	if ((c_files % i_per_page) > 0):
		c_available_pages += 1



	
	for r in cursor:
		json_response_data['files'].update({r['file_id']:{"id": r['file_id'], "tags": r["tags"]}})


	time_end = time.time()
	i_search_milliseconds = (time_end - time_start) * 1000

	#l_distinct = cursor.distinct("tags", {'tag.type': 'directory.word'})
	#l_distinct = cursor.distinct("tags", {"tag.type": "directory.word"})
	#l_distinct = cursor.aggregate([
	#	{"$unwind": "tags"},
	#	{"$group": {"_id": "$tags", "count": {"$sum": 1}}},
	#	{"$sort": SON([("count", -1), ("_id", -1)])}
	#	])
	
	#l_distinct = cursor.distinct("tags", "{'type': 'directory.word'}")
	l_distinct = cursor.distinct("tags")

	l_filter_distinct = []
	c_distinct = 0

	for c_index, tag in enumerate(l_distinct):
		if tag["type"] == "filter.value":
			l_filter_distinct.append({ "term": tag["value"]})
			c_distinct += 1

	json_response_data["results_info"] = {"count": c_files, "available_pages": c_available_pages, "speed": i_search_milliseconds, "distinct": l_filter_distinct}

	s_response = json.dumps(json_response_data)

	http_response = HttpResponse(s_response, content_type="application/json")
	http_response['Access-Control-Allow-Origin'] = '*'
	return http_response