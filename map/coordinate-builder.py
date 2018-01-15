import json


# full map
min_x = -150
min_y = -150
max_x = 150
max_y = 150

# test coords
#min_x = 50
#min_y = 0
#max_x = 120
#max_y = 50


def old_cluster_approach():
	# i was just going to get 25x25 squares, walking through
	# all of the land in clusters.  then, i decided that was
	# dumb since i can just grab arbitrary coord data.  dude
	# swapping to just pulling rows!  this function is a 
	# bunch of garbage right now.  ignore!

	cluster_size = 25

	cluster_start_x = min_x
	cluster_start_y = min_y
	cluster_stop_x = cluster_start_x + cluster_size
	cluster_stop_y = cluster_start_y + cluster_size

	# prime the starts
	current_x = cluster_start_x
	current_y = cluster_start_y

	while cluster_start_x <= max_x:
		print "checking cluster_start_x: %s" % cluster_start_x

		while cluster_start_y <= max_y:
			print "checking cluster_start_y: %s" % cluster_start_x

			# grab all the cluster coords
			while current_x <= cluster_stop_x:
				while current_y <= cluster_stop_y:

					print "%s,%s" % (current_x,current_y)

					current_y += 1
				current_x += 1

			# move to the next y cluster
			cluster_start_y = cluster_stop_y + 1
			cluster_stop_y = cluster_start_y + cluster_size

			if cluster_stop_y > max_y:
				cluster_stop_y = max_y

			current_y = cluster_start_y
			current_x = cluster_start_x

		# move to the next x cluster
		cluster_start_x = cluster_stop_x + 1
		cluster_stop_x = cluster_start_x + cluster_size

		if cluster_stop_x > max_x:
			cluster_stop_x = max_x

		# reset the y cluster
		cluster_start_y = min_y
		cluster_stop_y = cluster_start_y + cluster_size


def generate_row_json():
	rows_per_batch = 3

	row_start_y = min_y
	row_stop_y = row_start_y + rows_per_batch - 1
	
	while row_start_y <= max_y:
		print "====> assembling rows %s-%s, inclusive" % (row_start_y, row_stop_y)

		batch = {"coordinates":[]}

		current_y = row_start_y
		while current_y <= row_stop_y:

			# loop through ALL the x coords
			current_x = min_x
			while current_x <= max_x:

				# these are our coords:  current_x,current_y
				#print "%s,%s" % (current_x,current_y)

				batch["coordinates"].append("%s,%s" % (current_x,current_y))

				current_x += 1


			# next row in the batch!
			current_y += 1


		# handle the batch persistence.
		f = open("cache/coords_row_" + str(row_start_y) + "_to_" + str(row_stop_y) + ".json", 'wb')
		f.write(json.dumps(batch))
		f.close()


		# next batch!
		row_start_y += rows_per_batch
		row_stop_y += rows_per_batch

		if row_stop_y >= max_y:
			row_stop_y = max_y
		


def generate_min_max_urls():

	urls = []

	rows_per_batch = 1

	row_start_y = min_y
	row_stop_y = row_start_y + rows_per_batch - 1
	
	while row_start_y <= max_y:
		query_url = "https://api.auction.decentraland.org/api/parcelState/range/%s,%s/%s,%s" % (min_x,row_start_y,max_x,row_stop_y)
		print query_url
		urls.append(query_url)

		# next batch!
		row_start_y += rows_per_batch
		row_stop_y += rows_per_batch

		if row_stop_y >= max_y:
			row_stop_y = max_y
		

	# handle the batch persistence.
	f = open("cache/urls_min_max.json", 'wb')
	f.write(json.dumps(urls))
	f.close()



# let's build us some json coords!
generate_min_max_urls()


