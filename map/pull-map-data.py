import os, sys
import urllib2
import json
import csv
import hashlib
from sys import version_info
from datetime import datetime
import time
import dateutil.parser

# bidder info
# https://api.auction.decentraland.org/api/addressStats/0x0727fc3970cca8a5e57145777133dc551c124beb?params=%7B%7D

def getUserData(questionString):
	py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2
	if py3:
		response = input(questionString + ": ")
	else:
		response = raw_input(questionString + ": ")

	return response


def load_map_urls():
	print "\nfetching map range urls from disk\n"
	print "if you need to build them, run the coordinate-builder.py script\n"
	file = open("cache/urls_min_max.json", 'r')
	range_url_data = json.loads(file.read())
	file.close()

	return range_url_data


def load_projects():
	print "\nfetching projects from disk\n"
	print "if you need to download them, grab them here:\n"
	print "https://api.auction.decentraland.org/api/projects\n"

	file = open("cache/projects.json", 'r')
	project_data = json.loads(file.read())
	file.close()

	return project_data


def fetch_get_map_data(fetch_live, urls, project_data):
	# note:  this fetches data from the bottom-to-top, left-to-right.
	# should be 301 requests

	map = []

	for url in urls:

		map_row = []
		parcels = {"ok":True,"data":[]}

		cache_key = hashlib.md5(url).hexdigest()

		log_out("\npulling " + url + " as " + cache_key + "\n")

		if not fetch_live and os.path.isfile("cache/" + cache_key + ".json"):
			log_out( "fetching parcels from CACHE\n")
			file = open("cache/" + cache_key + ".json", 'r')
			parcels = json.loads(file.read())
			file.close()

		else:
			response = urllib2.urlopen(url)
			parcels = json.load(response)   
		
			f = open("cache/" + cache_key + ".json", 'wb')
			f.write(json.dumps(parcels))
			f.close()
		

		if parcels['ok']:

			parcel_row = []

			# transform it into usable map data.
			# we care about:
			# 1) id
			# 2) owner
			# 3) price/value
			# 4) land or district (to make things easy)

			for parcel in parcels['data']:
				parcel_data = {}

				parcel_data['id'] = parcel['id']
				parcel_data['home'] = parcel['id']
				parcel_data['x'] = int(parcel['id'].split(',')[0])
				parcel_data['y'] = int(parcel['id'].split(',')[1])

				# btw, i'm not a fan of debugging ternary notation
				if parcel['amount'] is not None:
					parcel_data['value'] = int(parcel['amount'])
				else:
					parcel_data['value'] = 1000
				
				if parcel['address'] is not None:
					parcel_data['owner'] = parcel['address']
					parcel_data['type'] = "Land"

				else:
					if parcel['projectId'] is not None:
						project = lookup_project_data(project_data, parcel['projectId'])

						parcel_data['owner'] = project['name']

						if parcel['projectId'] == "55327350-d9f0-4cae-b0f3-8745a0431099":
							parcel_data['type'] = "Plaza"
							parcel_data['home'] = project['lookup']

						elif parcel['projectId'] == "f77140f9-c7b4-4787-89c9-9fa0e219b079":
							parcel_data['type'] = "Road"

						else:
							parcel_data['type'] = "District"
							parcel_data['home'] = project['lookup']

					else:
						parcel_data['owner'] = "Unclaimed"
						parcel_data['type'] = "Vacant"


				parcel_row.append(parcel_data)


			sorted_parcel_row = sorted(parcel_row, key=lambda k: k['x']) 

			map.insert(0, sorted_parcel_row)

			#break


	f = open("cache/map.json", 'wb')
	f.write(json.dumps(map, indent=4, sort_keys=True))
	f.close()

	return map


def lookup_project_data(project_data, id):
	for project in project_data['data']:
		if project['id'] == id:
			return project

	return None


def fetch_post_map_data(fetch_live, coordinate_data, cluster_name):
	if not fetch_live:
		print "\nfetching parcels from CACHE\n"
		file = open("cache/" + cluster_name + ".json", 'r')
		parcels = json.loads(file.read())
		file.close()

		return parcels

	print "fetching LIVE parcels"

	url = "https://api.auction.decentraland.org/api/parcelState/range"

	headers = {}
	headers["Pragma"] = "no-cache"
	headers["Origin"] = "https://auction.decentraland.org"
	headers["Accept-Encoding"] = "gzip, deflate, br"
	headers["Accept-Language"] = "en-US,en;q=0.9"
	headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
	headers["Content-Type"] = "application/json;charset=UTF-8"
	headers["Accept"] = "application/json, text/plain, */*"
	headers["Cache-Control"] = "no-cache"
	headers["Referer"] = "https://auction.decentraland.org/-7/-5"
	headers["Connection"] = "keep-alive"
	headers["DNT"] = "1"


	#data = '{"coordinates":["-23,-19","-23,-18","-23,-17","-23,-16","-23,-15","-23,-14","-23,-13","-23,-12","-23,-11","-23,-10","-23,-9","-23,-8","-23,-7","-23,-6","-23,-5","-23,-4","-23,-3","-23,-2","-23,-1","-23,0","-23,1","-23,2","-23,3","-23,4","-23,5","-23,6","-23,7","-23,8","-23,9","-22,-19","-22,-18","-22,-17","-22,-16","-22,-15","-22,-14","-22,-13","-22,-12","-22,-11","-22,-10","-22,-9","-22,-8","-22,-7","-22,-6","-22,-5","-22,-4","-22,-3","-22,-2","-22,-1","-22,0","-22,1","-22,2","-22,3","-22,4","-22,5","-22,6","-22,7","-22,8","-22,9","-21,-19","-21,-18","-21,-17","-21,-16","-21,-15","-21,-14","-21,-13","-21,-12","-21,-11","-21,-10","-21,-9","-21,-8","-21,-7","-21,-6","-21,-5","-21,-4","-21,-3","-21,-2","-21,-1","-21,0","-21,1","-21,2","-21,3","-21,4","-21,5","-21,6","-21,7","-21,8","-21,9","-20,-19","-20,-18","-20,-17","-20,-16","-20,-15","-20,-14","-20,-13","-20,-12","-20,-11","-20,-10","-20,-9","-20,-8","-20,-7","-20,-6","-20,-5","-20,-4","-20,-3","-20,-2","-20,-1","-20,0","-20,1","-20,2","-20,3","-20,4","-20,5","-20,6","-20,7","-20,8","-20,9","-19,-19","-19,-18","-19,-17","-19,-16","-19,-15","-19,-14","-19,-13","-19,-12","-19,-11","-19,-10","-19,-9","-19,-8","-19,-7","-19,-6","-19,-5","-19,-4","-19,-3","-19,-2","-19,-1","-19,0","-19,1","-19,2","-19,3","-19,4","-19,5","-19,6","-19,7","-19,8","-19,9","-18,-19","-18,-18","-18,-17","-18,-16","-18,-15","-18,-14","-18,-13","-18,-12","-18,-11","-18,-10","-18,-9","-18,-8","-18,-7","-18,-6","-18,-5","-18,-4","-18,-3","-18,-2","-18,-1","-18,0","-18,1","-18,2","-18,3","-18,4","-18,5","-18,6","-18,7","-18,8","-18,9","-17,-19","-17,-18","-17,-17","-17,-16","-17,-15","-17,-14","-17,-13","-17,-12","-17,-11","-17,-10","-17,-9","-17,-8","-17,-7","-17,-6","-17,-5","-17,-4","-17,-3","-17,-2","-17,-1","-17,0","-17,1","-17,2","-17,3","-17,4","-17,5","-17,6","-17,7","-17,8","-17,9","-16,-19","-16,-18","-16,-17","-16,-16","-16,-15","-16,-14","-16,-13","-16,-12","-16,-11","-16,-10","-16,-9","-16,-8","-16,-7","-16,-6","-16,-5","-16,-4","-16,-3","-16,-2","-16,-1","-16,0","-16,1","-16,2","-16,3","-16,4","-16,5","-16,6","-16,7","-16,8","-16,9","-15,-19","-15,-18","-15,-17","-15,-16","-15,-15","-15,-14","-15,-13","-15,-12","-15,-11","-15,-10","-15,-9","-15,-8","-15,-7","-15,-6","-15,-5","-15,-4","-15,-3","-15,-2","-15,-1","-15,0","-15,1","-15,2","-15,3","-15,4","-15,5","-15,6","-15,7","-15,8","-15,9","-14,-19","-14,-18","-14,-17","-14,-16","-14,-15","-14,-14","-14,-13","-14,-12","-14,-11","-14,-10","-14,-9","-14,-8","-14,-7","-14,-6","-14,-5","-14,-4","-14,-3","-14,-2","-14,-1","-14,0","-14,1","-14,2","-14,3","-14,4","-14,5","-14,6","-14,7","-14,8","-14,9","-13,-19","-13,-18","-13,-17","-13,-16","-13,-15","-13,-14","-13,-13","-13,-12","-13,-11","-13,-10","-13,-9","-13,-8","-13,-7","-13,-6","-13,-5","-13,-4","-13,-3","-13,-2","-13,-1","-13,0","-13,1","-13,2","-13,3","-13,4","-13,5","-13,6","-13,7","-13,8","-13,9","-12,-19","-12,-18","-12,-17","-12,-16","-12,-15","-12,-14","-12,-13","-12,-12","-12,-11","-12,-10","-12,-9","-12,-8","-12,-7","-12,-6","-12,-5","-12,-4","-12,-3","-12,-2","-12,-1","-12,0","-12,1","-12,2","-12,3","-12,4","-12,5","-12,6","-12,7","-12,8","-12,9","-11,-19","-11,-18","-11,-17","-11,-16","-11,-15","-11,-14","-11,-13","-11,-12","-11,-11","-11,-10","-11,-9","-11,-8","-11,-7","-11,-6","-11,-5","-11,-4","-11,-3","-11,-2","-11,-1","-11,0","-11,1","-11,2","-11,3","-11,4","-11,5","-11,6","-11,7","-11,8","-11,9","-10,-19","-10,-18","-10,-17","-10,-16","-10,-15","-10,-14","-10,-13","-10,-12","-10,-11","-10,-10","-10,-9","-10,-8","-10,-7","-10,-6","-10,-5","-10,-4","-10,-3","-10,-2","-10,-1","-10,0","-10,1","-10,2","-10,3","-10,4","-10,5","-10,6","-10,7","-10,8","-10,9","-9,-19","-9,-18","-9,-17","-9,-16","-9,-15","-9,-14","-9,-13","-9,-12","-9,-11","-9,-10","-9,-9","-9,-8","-9,-7","-9,-6","-9,-5","-9,-4","-9,-3","-9,-2","-9,-1","-9,0","-9,1","-9,2","-9,3","-9,4","-9,5","-9,6","-9,7","-9,8","-9,9","-8,-19","-8,-18","-8,-17","-8,-16","-8,-15","-8,-14","-8,-13","-8,-12","-8,-11","-8,-10","-8,-9","-8,-8","-8,-7","-8,-6","-8,-5","-8,-4","-8,-3","-8,-2","-8,-1","-8,0","-8,1","-8,2","-8,3","-8,4","-8,5","-8,6","-8,7","-8,8","-8,9","-7,-19","-7,-18","-7,-17","-7,-16","-7,-15","-7,-14","-7,-13","-7,-12","-7,-11","-7,-10","-7,-9","-7,-8","-7,-7","-7,-6","-7,-5","-7,-4","-7,-3","-7,-2","-7,-1","-7,0","-7,1","-7,2","-7,3","-7,4","-7,5","-7,6","-7,7","-7,8","-7,9","-6,-19","-6,-18","-6,-17","-6,-16","-6,-15","-6,-14","-6,-13","-6,-12","-6,-11","-6,-10","-6,-9","-6,-8","-6,-7","-6,-6","-6,-5","-6,-4","-6,-3","-6,-2","-6,-1","-6,0","-6,1","-6,2","-6,3","-6,4","-6,5","-6,6","-6,7","-6,8","-6,9","-5,-19","-5,-18","-5,-17","-5,-16","-5,-15","-5,-14","-5,-13","-5,-12","-5,-11","-5,-10","-5,-9","-5,-8","-5,-7","-5,-6","-5,-5","-5,-4","-5,-3","-5,-2","-5,-1","-5,0","-5,1","-5,2","-5,3","-5,4","-5,5","-5,6","-5,7","-5,8","-5,9","-4,-19","-4,-18","-4,-17","-4,-16","-4,-15","-4,-14","-4,-13","-4,-12","-4,-11","-4,-10","-4,-9","-4,-8","-4,-7","-4,-6","-4,-5","-4,-4","-4,-3","-4,-2","-4,-1","-4,0","-4,1","-4,2","-4,3","-4,4","-4,5","-4,6","-4,7","-4,8","-4,9","-3,-19","-3,-18","-3,-17","-3,-16","-3,-15","-3,-14","-3,-13","-3,-12","-3,-11","-3,-10","-3,-9","-3,-8","-3,-7","-3,-6","-3,-5","-3,-4","-3,-3","-3,-2","-3,-1","-3,0","-3,1","-3,2","-3,3","-3,4","-3,5","-3,6","-3,7","-3,8","-3,9","-2,-19","-2,-18","-2,-17","-2,-16","-2,-15","-2,-14","-2,-13","-2,-12","-2,-11","-2,-10","-2,-9","-2,-8","-2,-7","-2,-6","-2,-5","-2,-4","-2,-3","-2,-2","-2,-1","-2,0","-2,1","-2,2","-2,3","-2,4","-2,5","-2,6","-2,7","-2,8","-2,9","-1,-19","-1,-18","-1,-17","-1,-16","-1,-15","-1,-14","-1,-13","-1,-12","-1,-11","-1,-10","-1,-9","-1,-8","-1,-7","-1,-6","-1,-5","-1,-4","-1,-3","-1,-2","-1,-1","-1,0","-1,1","-1,2","-1,3","-1,4","-1,5","-1,6","-1,7","-1,8","-1,9","0,-19","0,-18","0,-17","0,-16","0,-15","0,-14","0,-13","0,-12","0,-11","0,-10","0,-9","0,-8","0,-7","0,-6","0,-5","0,-4","0,-3","0,-2","0,-1","0,0","0,1","0,2","0,3","0,4","0,5","0,6","0,7","0,8","0,9","1,-19","1,-18","1,-17","1,-16","1,-15","1,-14","1,-13","1,-12","1,-11","1,-10","1,-9","1,-8","1,-7","1,-6","1,-5","1,-4","1,-3","1,-2","1,-1","1,0","1,1","1,2","1,3","1,4","1,5","1,6","1,7","1,8","1,9","2,-19","2,-18","2,-17","2,-16","2,-15","2,-14","2,-13","2,-12","2,-11","2,-10","2,-9","2,-8","2,-7","2,-6","2,-5","2,-4","2,-3","2,-2","2,-1","2,0","2,1","2,2","2,3","2,4","2,5","2,6","2,7","2,8","2,9","3,-19","3,-18","3,-17","3,-16","3,-15","3,-14","3,-13","3,-12","3,-11","3,-10","3,-9","3,-8","3,-7","3,-6","3,-5","3,-4","3,-3","3,-2","3,-1","3,0","3,1","3,2","3,3","3,4","3,5","3,6","3,7","3,8","3,9","4,-19","4,-18","4,-17","4,-16","4,-15","4,-14","4,-13","4,-12","4,-11","4,-10","4,-9","4,-8","4,-7","4,-6","4,-5","4,-4","4,-3","4,-2","4,-1","4,0","4,1","4,2","4,3","4,4","4,5","4,6","4,7","4,8","4,9","5,-19","5,-18","5,-17","5,-16","5,-15","5,-14","5,-13","5,-12","5,-11","5,-10","5,-9","5,-8","5,-7","5,-6","5,-5","5,-4","5,-3","5,-2","5,-1","5,0","5,1","5,2","5,3","5,4","5,5","5,6","5,7","5,8","5,9","6,-19","6,-18","6,-17","6,-16","6,-15","6,-14","6,-13","6,-12","6,-11","6,-10","6,-9","6,-8","6,-7","6,-6","6,-5","6,-4","6,-3","6,-2","6,-1","6,0","6,1","6,2","6,3","6,4","6,5","6,6","6,7","6,8","6,9","7,-19","7,-18","7,-17","7,-16","7,-15","7,-14","7,-13","7,-12","7,-11","7,-10","7,-9","7,-8","7,-7","7,-6","7,-5","7,-4","7,-3","7,-2","7,-1","7,0","7,1","7,2","7,3","7,4","7,5","7,6","7,7","7,8","7,9","8,-19","8,-18","8,-17","8,-16","8,-15","8,-14","8,-13","8,-12","8,-11","8,-10","8,-9","8,-8","8,-7","8,-6","8,-5","8,-4","8,-3","8,-2","8,-1","8,0","8,1","8,2","8,3","8,4","8,5","8,6","8,7","8,8","8,9","9,-19","9,-18","9,-17","9,-16","9,-15","9,-14","9,-13","9,-12","9,-11","9,-10","9,-9","9,-8","9,-7","9,-6","9,-5","9,-4","9,-3","9,-2","9,-1","9,0","9,1","9,2","9,3","9,4","9,5","9,6","9,7","9,8","9,9"]}'
	data = json.dumps({"coordinates":coordinate_data})

	req = urllib2.Request(url, data, headers)

	u = urllib2.urlopen(req)
	response = u.read()
	u.close()

	parcels = json.loads(response)
	if not parcels['ok']:
		log_out("ERROR FETCHING DATA: " + parcels['error'])
		return parcels

	f = open("cache/" + cluster_name + ".json", 'wb')
	f.write(response)
	f.close()

	return parcels

def datetime_from_utc_to_local(datestring):
	utc_datetime = dateutil.parser.parse(datestring)
	now_timestamp = time.time()
	offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
	return utc_datetime + offset

def log_out(logline):
	global log_data
	log_data += "\n" + logline
	print logline


def string_to_color(my_string):
	# trying to figure out how i want to do this coloring thing.
	c = "api.auction.decentraland.org".encode("hex")
	int_array = [int(c[i:i+2],16) for i in range(0,len(c),2)]


	return True





log_data = ""
use_live_parcels = False
user_response = getUserData("Pull live data? (y/n)")
if user_response.lower() == "y":
	use_live_parcels = True
else:
	use_live_parcels = False


print ""

#print json.dumps(cluster_coords)

log_out("")
log_out("")
log_out("=================================================================")
log_out("=================================================================")
log_out("New Log Run for pulling map data")
log_out(datetime.today().strftime("%c"))
if use_live_parcels:
	log_out("LIVE DATA")
else:
	log_out("CACHED DATA")
log_out("-----------------------------------------------------------------")
log_out("")

#parcels = fetch_map_data(use_live_parcels, cluster_coords, clusters[cluster_index]['name'])

map_urls = load_map_urls()
map = fetch_get_map_data(use_live_parcels, map_urls, load_projects())


log_out("-----------------------------------------------------------------")
log_out("=================================================================")
log_out("")
log_out("")


# dump the logfile.
with open("log_data.log", "a") as logfile:
	logfile.write(log_data)

