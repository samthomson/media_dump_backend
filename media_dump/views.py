from django.http import HttpResponse

import pymongo
from pymongo import MongoClient

def index(request):

	s_query = ""
	i_page = "1"

	if request.GET['query'] != None:
		s_query = request.GET['query']

	if request.GET['page'] != None:
		i_page = request.GET['page']


	mongo_client = MongoClient()
	# get mongo database
	mongo_db = mongo_client.media_dump
	# get files collection (table)
	cursor = mongo_db.files.find({tags: { $elemMatch: { value: s_query } } } )

	s_result = ""

	for r in cursor:
		s_result = s_result + r['file_id']



	return HttpResponse("searching for %s, page %s.\n%s" % (s_query, i_page, s_result))