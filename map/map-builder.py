import json
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import textwrap
#>>> strs = "In my project, I have a bunch of strings that are read in from a file. Most of them, when printed in the command console, exceed 80 characters in length and wrap around, looking ugly."
#>>> print(textwrap.fill(strs, 20))


log_data = ""

# btw, we're assuming the world is square.
tile_size = 25
wide_border = 2
thin_border = 1
dark_every = 10

my_color = "PaleGoldenRod"
neighbor_color = "black"
land_color = "DarkSeaGreen"
land_font_color = "black"
district_color = "MediumPurple"
district_font_color = "white"
vacant_color = "PapayaWhip"
road_color = "DimGray"
plaza_color = "White"
plaza_font_color = "DimGray"

labelFontSmall = ImageFont.truetype("RobotoCondensed-Bold.ttf", 30)
labelFontLarge = ImageFont.truetype("RobotoCondensed-Bold.ttf", 60)
max_characters = 15


# for making your own custom map.
highlight_color = "Crimson"
highlight_owner = "0xccd5089557ae6a2ba063e8720e725a6bf743b3e8"



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

			if tile_data['owner'] == highlight_owner:
				fill_color = highlight_color

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
			#log_out("%s, %s, %s, %s" % (row_counter, len(row_data) - 1, row_counter + 1, len(map_data)))
			if row_counter + 1 < len(map_data) and row_counter < len(row_data) - 1 and map_data[row_counter + 1][col_counter]['owner'] == tile_data['owner']:
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
	label_data = {}

	# draw the tiles first.
	# oh, and grab label data as we go.
	row_counter = 0
	for row_data in map_data:

		col_counter = 0
		for tile_data in row_data:

			tile_image = Image.open("dist/tile_%s_%s.png" % (tile_data['x'],tile_data['y']))
			map_image.paste(tile_image, (tile_size * col_counter, tile_size * row_counter))

			if tile_data['owner'] not in label_data:
				label_data[tile_data['owner']] = {}
				label_data[tile_data['owner']]['count'] = 0
				label_data[tile_data['owner']]['max_x'] = -999999
				label_data[tile_data['owner']]['max_y'] = -999999
				label_data[tile_data['owner']]['min_x'] = 999999
				label_data[tile_data['owner']]['min_y'] = 999999

			label_data[tile_data['owner']]['count'] += 1
			
			if tile_data['x'] < label_data[tile_data['owner']]['min_x']:
				label_data[tile_data['owner']]['min_x'] = tile_data['x']

			if tile_data['x'] > label_data[tile_data['owner']]['max_x']:
				label_data[tile_data['owner']]['max_x'] = tile_data['x']

			if tile_data['y'] < label_data[tile_data['owner']]['min_y']:
				label_data[tile_data['owner']]['min_y'] = tile_data['y']

			if tile_data['y'] > label_data[tile_data['owner']]['max_y']:
				label_data[tile_data['owner']]['max_y'] = tile_data['y']

			col_counter += 1

		row_counter += 1


	# then draw the labels.
	dr = ImageDraw.Draw(map_image)
	row_counter = 0
	for row_data in map_data:

		col_counter = 0
		for tile_data in row_data:
			label = ""
			labelFont = labelFontLarge
			fill_color = land_font_color
			is_large_area = label_data[tile_data['owner']]['count'] > 250

			# setup for districts
			if tile_data['type'] == "District":
				fill_color = district_font_color
				if tile_data['home'] == tile_data['id']:
					label = textwrap.fill(tile_data['owner'], max_characters)
					if not is_large_area:
						labelFont = labelFontSmall

			# setup for plazas
			elif tile_data['type'] == "Plaza":
				fill_color = plaza_font_color
				if tile_data['home'] == tile_data['id']:
					label = tile_data['owner']

			# setup for whales
			# temporarily disabled because most of them own more than one chunk of contiguous parcels.
			# gonna have to make another batch of passes through the whales looking specifically
			# for large contiguous plots and then home them.  _sigh_  maybe later.
			elif False and label_data[tile_data['owner']]['count'] > 150:
				# we should probably bake their home into the map data, but, whatever.
				# figure out their home.
				# basically, if most of their parcels are in the same area, draw in the middle of that.
				rough_width = label_data[tile_data['owner']]['max_x'] - label_data[tile_data['owner']]['min_x']
				rough_height = label_data[tile_data['owner']]['max_y'] - label_data[tile_data['owner']]['min_y']

				if rough_width * rough_height * .6 <= label_data[tile_data['owner']]['count']:
					# most of their land is contiguous
					if "%s,%s" % (int((label_data[tile_data['owner']]['max_x'] + label_data[tile_data['owner']]['min_x'])/2), int((label_data[tile_data['owner']]['max_y'] + label_data[tile_data['owner']]['min_y'])/2)) == tile_data['id']:
						label = tile_data['owner'][0:8]


			if label != "":
				# this "getsize" method has a bug with multi-line text.  compensating!
				label_lines = label.split("\n")
				x_offset, y_offset = labelFont.getsize(label_lines[0])
				dr.text((tile_size * (col_counter) - (int(x_offset/2)), tile_size * row_counter - (int(y_offset/2) * len(label_lines))), label, font=labelFont, fill=fill_color)

			col_counter += 1

		row_counter += 1


	map_image.save("dist/decentraland_map.png")


def log_out(logline):
	global log_data
	log_data += "\n" + logline
	print logline


map_data = load_map()
build_tiles(map_data)
assemble_tile_images(map_data)


# dump the logfile.
with open("log_data.log", "a") as logfile:
	logfile.write(log_data)

