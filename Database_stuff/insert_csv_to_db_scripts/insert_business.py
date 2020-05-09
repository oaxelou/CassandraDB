from cassandra.cluster import Cluster
import csv
import time,datetime

cluster = Cluster()
session = cluster.connect('recommedations_keyspace')

category_types=[]
with open('business.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count=0
	for row in csv_reader:
		'''if line_count==0:
			colcounter=0
			for col in row:
				print colcounter, ":", col
				colcounter+=1'''
		if line_count>0:
			perform_query=True
			query_table1="insert into business_by_id"
			query_table2="insert into business_by_city"
			query_columns="(" 
			query_values=") values("
			
			# BUSINESSID
			if not row[0]:
				print line_count, "The primary key (businessid) should not be null. This row is omitted"
				print row
				perform_query=False
			else:
				businessid=row[0]
				# print "businessid:", businessid
				query_columns += "businessid"
				query_values += "'" + businessid + "'"
			
			# NAME
			if row[1]:
				name=row[1]
				# print "name:", name
				query_columns += ",name"
				query_values += ",'" + name.replace("'", "''") + "'"
			
			# ADDRESS
			if row[2]:
				address=row[2].replace("'", "''")
				# print "address:", address
				query_columns += ",address"
				query_values += ",'" + address + "'"
			
			# CITY
			if not row[3]:
				print line_count, "The primary key (city) should not be null. This row is omitted"
				print row
				perform_query=False
			else:
				city=row[3].replace("'", "''")
				# print "city:", city
				query_columns += ",city"
				query_values += ",'" + city + "'"
			
			if perform_query:
				# STATE
				if row[4]:
					state=row[4]
					# print "state:", state
					query_columns += ",state"
					query_values += ",'" + state + "'"
				
				# POSTAL CODE
				if row[5]:
					postal_code=row[5]
					# print "postal_code:", postal_code
					query_columns += ",postal_code"
					query_values += ",'" + postal_code + "'"
				
				# COORDINATES (LATITUDE, LONGTITUDE)
				if row[6] and row[7]:
					coordinates=(float(row[6]), float(row[7]))
					# print "coordinates:", coordinates
					query_columns += ",coordinates"
					query_values += ",{'latitude':" + str(coordinates[0]) + ",'longtitude':" + str(coordinates[1]) + "}"
				
				# STARS
				if row[8]:
					stars=float(row[8])
					# print "stars:", stars
					query_columns += ",stars"
					query_values += "," + str(stars) + ""
				
				# REVIEW COUNT
				if row[9]:
					review_count=int(float(row[9]))
					# print "review_count:", review_count
					query_columns += ",review_count"
					query_values += "," + str(review_count) + ""
				
				# CATEGORIES
				if row[10]:
					categories=row[10].replace("'", "''").split(', ')
					# print "categories:", categories
					query_columns += ",categories"
					query_values+= ",{'"
					for category in categories[:-1]:
						query_values += category + "','"
					query_values+=categories[-1]
					query_values+="'}"
				
				# HOURS PER DAY
				days={0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
				query_columns += ",hours"
				query_values += ",{"
				for i in range(11,17):
					# print "Checking day:", days[i-11]
					query_values+="'" + days[i-11] + "':"
					query_values+="'" + row[i] + "',"
				# print "Checking day:", days[17-11]
				query_values+="'" + days[17-11] + "':"
				query_values+="'" + row[17] + "'"
				query_values+="}"

				# GENERAL ATTRIBUTES
				attr={0:"by_appointment_only", 1:"business_accepts_credit_cards", 2:"business_accepts_bitcoin", 3:"has_tv", 4:"wifi", 5:"alcohol", 6:"happyhour", 7:"good_for_dancing", 8:"restaurants_reservations", 9:"caters", 10:"restaurants_takeout", 11:"restaurants_good_for_groups", 12:"restaurants_delivery", 13:"drivethru", 14:"restaurants_pricerange", 15:"outdoorseating", 16:"bikeparking", 17:"wheelchair_accessible", 18:"dogsallowed", 19:"goodforkids", 20:"noiselevel"}
				query_columns += ",general_attributes"
				query_values += ",{"
				for i in range(18,38):
					# print "Checking attribute:", attr[i-18]
					query_values+="'" + attr[i-18] + "':"
					query_values+="'" + row[i] + "',"
				# print "Checking attribute:", attr[38-18]
				query_values+="'" + attr[38-18] + "':"
				query_values+="'" + row[38] + "'"
				query_values+="}"
				
				# GOOD FOR MEAL
				meals={0:"dinner", 1:"breakfast", 2:"brunch", 3:"lunch", 4:"dessert", 5:"latenight"}
				query_columns += ",good_for_meal"
				query_values += ",{"
				for i in range(39,44):
					# print "Checking meal:", meals[i-39]
					query_values+="'" + meals[i-39] + "':"
					query_values+="'" + row[i] + "',"
				# print "Checking attribute:", meals[44-39]
				query_values+="'" + meals[44-39] + "':"
				query_values+="'" + row[44] + "'"
				query_values+="}"
				
				# BUSINESS PARKING
				parking={0:"garage", 1:"street", 2:"validated", 3:"lot", 4:"valet"}
				query_columns += ",business_parking"
				query_values += ",{"
				for i in range(45,49):
					# print "Checking meal:", parking[i-45]
					query_values+="'" + parking[i-45] + "':"
					query_values+="'" + row[i] + "',"
				# print "Checking attribute:", parking[49-45]
				query_values+="'" + parking[49-45] + "':"
				query_values+="'" + row[49] + "'"
				query_values+="}"
				
				# AMBIENCE
				ambience={0:"romantic",1:"intimate",2:"classy",3:"hipster",4:"divey",5:"touristy",6:"trendy",7:"upscale",8:"casual"}
				query_columns += ",ambience"
				query_values += ",{"
				for i in range(50,58):
					# print "Checking ambience:", ambience[i-50]
					query_values+="'" + ambience[i-50] + "':"
					query_values+="'" + row[i] + "',"
				# print "Checking attribute:", ambience[58-50]
				query_values+="'" + ambience[58-50] + "':"
				query_values+="'" + row[58] + "'"
				query_values+="}"
				
				# MUSIC
				music={0:"dj",1:"background_music",2:"no_music",3:"karaoke",4:"live",5:"video",6:"jukebox"}
				query_columns += ",music"
				query_values += ",{"
				for i in range(59,65):
					# print "Checking music:", music[i-59]
					query_values+="'" + music[i-59] + "':"
					query_values+="'" + row[i] + "',"
				# print "Checking attribute:", music[65-59]
				query_values+="'" + music[65-59] + "':"
				query_values+="'" + row[65] + "'"
				query_values+="}"
				
				
				query_values+=");"			
				# print query_table1 + query_columns + query_values
				# print "----------------------------------------------"
				# print query_table2 + query_columns + query_values
				session.execute(query_table1 + query_columns + query_values)
				session.execute(query_table2 + query_columns + query_values)
			#exit()
		if line_count % 10000 == 0:
			print str(line_count) + " " + str(datetime.datetime.now().strftime("%H:%M:%S"))
		line_count+=1
	print "Processed ", line_count, " lines."
