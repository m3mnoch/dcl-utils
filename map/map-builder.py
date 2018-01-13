import json
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

log_data = ""

# btw, we're assuming the world is square.
tile_size = 25
wide_border = 2
thin_border = 1
dark_every = 10

my_color = "PaleGoldenRod"
neighbor_color = "black"
land_color = "DarkSeaGreen"
district_color = "MediumPurple"
vacant_color = "PapayaWhip"
road_color = "DimGray"
plaza_color = "White"

labelFont = ImageFont.truetype("RobotoCondensed-Bold.ttf", 30)



def load_map():
	log_out("fetching map data from CACHE\n")
	#file = open("test_map.json", 'r')
	file = open("cache/map.json", 'r')
	map_data = json.loads(file.read())
	file.close()

	return map_data


def build_tiles(map_data):
	log_out( "building individual tile images\n")
	# map data is top-to-bottom, left-to-right
	# basically, -150,150 diagonally to 150,-150
	# or, a more normal cartesian quadrant iv, 0,0 to 300,300

	x1 = 0
	y1 = 0
	x2 = tile_size
	y2 = tile_size

	row_counter = 0
	for row_data in map_data:

		col_counter = 0
		for tile_data in row_data:

			fill_color = land_color

			if tile_data['type'] == "District":
				fill_color = district_color

			elif tile_data['type'] == "Plaza":
				fill_color = plaza_color

			elif tile_data['type'] == "Road":
				fill_color = road_color

			elif tile_data['type'] == "Vacant":
				fill_color = vacant_color

			base_tile = Image.new("RGB", (tile_size, tile_size))
			dr = ImageDraw.Draw(base_tile)
			dr.rectangle((x1,y1,x2,y2), fill=fill_color)

			# we want to darken up every 10 tiles.
			if row_counter%dark_every == 0 or col_counter%dark_every == 0:
				enhancement_factor = .9
				enhancer = ImageEnhance.Brightness(base_tile)
				base_tile = enhancer.enhance(enhancement_factor)
				dr = ImageDraw.Draw(base_tile)

			# top border
			if row_counter > 0 and map_data[row_counter - 1][col_counter]['owner'] == tile_data['owner']:
				border_color = my_color
				border_width = thin_border
			else:
				border_color = neighbor_color
				border_width = wide_border
			line = (x1,y1,x2,y1)
			dr.line(line, fill=border_color, width=border_width)

			# right border
			if col_counter < len(row_data)-1 and map_data[row_counter][col_counter + 1]['owner'] == tile_data['owner']:
				border_color = my_color
				border_width = thin_border
			else:
				border_color = neighbor_color
				border_width = wide_border
			line = (x2,y1,x2,y2)
			dr.line(line, fill=border_color, width=border_width)

			# bottom border
			if row_counter < len(row_data) - 1 and map_data[row_counter + 1][col_counter]['owner'] == tile_data['owner']:
				border_color = my_color
				border_width = thin_border
			else:
				border_color = neighbor_color
				border_width = wide_border
			line = (x1,y2,x2,y2)
			dr.line(line, fill=border_color, width=border_width)

			# left border
			if col_counter > 0 and map_data[row_counter][col_counter - 1]['owner'] == tile_data['owner']:
				border_color = my_color
				border_width = thin_border
			else:
				border_color = neighbor_color
				border_width = wide_border
			line = (x1,y1,x1,y2)
			dr.line(line, fill=border_color, width=border_width)



			# export the tile for random use.
			base_tile.save("dist/tile_%s_%s.png" % (tile_data['x'],tile_data['y']))

			col_counter += 1

		row_counter += 1



def assemble_tile_images(map_data):
	log_out( "assembling all the tile images into a map.\n")

	map_image = Image.new("RGB", (tile_size * len(map_data[0]), tile_size * len(map_data)))

	# draw the tiles first.
	row_counter = 0
	for row_data in map_data:

		col_counter = 0
		for tile_data in row_data:

			tile_image = Image.open("dist/tile_%s_%s.png" % (tile_data['x'],tile_data['y']))
			map_image.paste(tile_image, (tile_size * col_counter, tile_size * row_counter))			

			col_counter += 1

		row_counter += 1


	# then draw the labels.
	dr = ImageDraw.Draw(map_image)
	row_counter = 0
	for row_data in map_data:

		col_counter = 0
		for tile_data in row_data:
			label = ""
			fill_color = land_color

			if tile_data['type'] == "District":
				fill_color = district_color
				if tile_data['home'] == tile_data['id']:
					label = tile_data['owner'].replace(" ", "\n")

			elif tile_data['type'] == "Plaza":
				fill_color = plaza_color
				if tile_data['home'] == tile_data['id']:
					label = tile_data['owner'].replace(" ", "\n")

			if label != "":
				dr.text((tile_size * col_counter, tile_size * row_counter), label, font=labelFont)

			col_counter += 1

		row_counter += 1


	map_image.save("dist/decentraland_map.png")


def log_out(logline):
	global log_data
	log_data += "\n" + logline


map_data = load_map()
build_tiles(map_data)
assemble_tile_images(map_data)


# dump the logfile.
with open("log_data.log", "a") as logfile:
	logfile.write(log_data)

print log_data

