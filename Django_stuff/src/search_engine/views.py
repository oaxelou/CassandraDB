# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from cassandra.cluster import Cluster
from datetime import datetime
import ast

cluster = Cluster()
session = cluster.connect('recommendations_keyspace')
 

# Create your views here.
def home(request):
	query_str="select distinct city from business_by_city;"
	rowRes=session.execute(query_str);
	cities=[]
	# print "\n\nCount:", len(rowRes.current_rows)
	for row in rowRes:
		cities.append(row.city) 
	# cities=['Olympia']
	context={'cities':cities, 'olympia':'Olympia'}
	return render(request, "home.html", context) # {}: context variables

def results(request):
	if request.method=="GET":
		# print request.GET.getlist('status')
		if 'city' in request.GET:
			print "Found city:",request.GET.get('city')
		else:
			print "SHOULD NEVER REACH THIS. city not in parameters"
			return HttpResponse("<h1>No city specified. No data to display!</h1>",{})

		# GET ALL POIS (GIVEN BY THE PARAMETERS) FROM DB BY THEIR businessid
		query_str="select * from business_by_city where city='" + request.GET['city'] + "';"
		rowRes=session.execute(query_str);
		pois=[]
		for row in rowRes:
			# Name
			pois.append({'name':row.name})
			# Categories
			pois[len(pois)-1]['categories']=[]
			if row.categories:
				for category in row.categories:
					pois[len(pois)-1]['categories'].append(str(category))
			# Hours
			hours=[]
			hours.append(('Mon',row.hours['Monday']))
			hours.append(('Tue',row.hours['Tuesday']))
			hours.append(('Wed',row.hours['Wednesday']))
			hours.append(('Thu',row.hours['Thursday']))
			hours.append(('Fri',row.hours['Friday']))
			hours.append(('Sat',row.hours['Saturday']))
			hours.append(('Sun',row.hours['Sunday']))
			pois[len(pois)-1]['hours']=hours
			# Stars
			pois[len(pois)-1]['stars']=row.stars
			pois[len(pois)-1]['review_count']=row.review_count
			# BUSINESSID
			pois[len(pois)-1]['businessid']=row.businessid

			# GENERAL ATTRIBUTES
			general_attributes=row.general_attributes
			# Noise Level
			pois[len(pois)-1]['noiselevel']=general_attributes['noiselevel']
			# Good for meal
			pois[len(pois)-1]['good_for_meal']=row.good_for_meal
			# Business parking
			pois[len(pois)-1]['business_parking']=row.business_parking
			# Ambience
			pois[len(pois)-1]['ambience']=row.ambience
			# Music
			pois[len(pois)-1]['music']=row.ambience

			# GENERAL ATTRIBUTS
			pois[len(pois)-1]['alcohol']=general_attributes['alcohol']
			pois[len(pois)-1]['bikeparking']=general_attributes['bikeparking']
			pois[len(pois)-1]['business_accepts_bitcoin']=general_attributes['business_accepts_bitcoin']
			pois[len(pois)-1]['business_accepts_credit_cards']=general_attributes['business_accepts_credit_cards']
			pois[len(pois)-1]['by_appointment_only']=general_attributes['by_appointment_only']
			pois[len(pois)-1]['caters']=general_attributes['caters']
			pois[len(pois)-1]['dogsallowed']=general_attributes['dogsallowed']
			pois[len(pois)-1]['drivethru']=general_attributes['drivethru']
			pois[len(pois)-1]['good_for_dancing']=general_attributes['good_for_dancing']
			pois[len(pois)-1]['goodforkids']=general_attributes['goodforkids']
			pois[len(pois)-1]['happyhour']=general_attributes['happyhour']
			pois[len(pois)-1]['outdoorseating']=general_attributes['outdoorseating']
			pois[len(pois)-1]['restaurants_delivery']=general_attributes['restaurants_delivery']
			pois[len(pois)-1]['restaurants_good_for_groups']=general_attributes['restaurants_good_for_groups']
			pois[len(pois)-1]['restaurants_pricerange']=general_attributes['restaurants_pricerange']
			pois[len(pois)-1]['restaurants_reservations']=general_attributes['restaurants_reservations']
			pois[len(pois)-1]['restaurants_takeout']=general_attributes['restaurants_takeout']
			pois[len(pois)-1]['wheelchair_accessible']=general_attributes['wheelchair_accessible']
			pois[len(pois)-1]['has_tv']=general_attributes['has_tv']
			pois[len(pois)-1]['wifi']=general_attributes['wifi']

		search_filters=[]
		# FILTER POIS BY THE CATEGORIES
		if 'categories' in request.GET:
			# print "Found categories:",request.GET.getlist('categories')
			categories=ast.literal_eval(request.GET.get('categories'))
			category_filtered_pois=[]
			categ_num=0
			for category in categories:
				if category in request.GET:
					search_filters.append("Category tag: " + category)
					categ_num+=1
					for poi in pois:
						if category in poi['categories'] and poi not in category_filtered_pois:
							category_filtered_pois.append(poi)
			if categ_num>0:
				pois=category_filtered_pois
			# else:
			# 	print "\n\nNO CATEGORIES DETERMINED"
		else:
			print "SHOULD NEVER REACH THIS. categories not in parameters"
			return HttpResponse("<h1>No categories specified. No data to display!</h1>",{})

		
		# FILTER POIS BY STAR RATING
		min_stars=0
		if 'one-star' in request.GET:
			min_stars=1
			search_filters.append("1 star")
		if 'two-stars' in request.GET:
			min_stars=2
			search_filters.append("2 stars")
		if 'three-stars' in request.GET:
			min_stars=3
			search_filters.append("3 stars")
		if 'four-stars' in request.GET:
			min_stars=4
			search_filters.append("4 stars")
		if 'five-stars' in request.GET:
			min_stars=5
			search_filters.append("5 stars")
		print "Should have minimum ", min_stars, " stars."
		
		min_stars_pois=[]
		for poi in pois:
			if min_stars<= poi['stars']:
				min_stars_pois.append(poi)
		pois=min_stars_pois

		# FILTER POIS BY NOISE LEVEL
		noise_levels=[]
		if 'quiet' in request.GET:noise_levels.append('quiet');search_filters.append("quiet")
		if 'average' in request.GET:noise_levels.append('average');search_filters.append("average")
		if 'loud' in request.GET:noise_levels.append('loud');search_filters.append("loud")
		if 'very-loud' in request.GET:noise_levels.append('very-loud');search_filters.append("very-loud")
		noise_level_pois=[]
		
		if noise_levels:
			for noise_level in noise_levels:
				for poi in pois:
					if noise_level==poi['noiselevel'] and poi not in noise_level_pois:
						print "found ", poi['name']
						noise_level_pois.append(poi)
			pois=noise_level_pois

		# FILTER POIS BY MEAL
		meals=[]
		if 'meal-breakfast' in request.GET:meals.append('breakfast');search_filters.append("meal: breakfast")
		if 'meal-brunch' in request.GET:meals.append('brunch');search_filters.append("meal: brunch")
		if 'meal-lunch' in request.GET:meals.append('lunch');search_filters.append("meal: lunch")
		if 'meal-dinner' in request.GET:meals.append('dinner');search_filters.append("meal: dinner")
		if 'meal-dessert' in request.GET:meals.append('dessert');search_filters.append("meal: dessert")
		if 'meal-latenight' in request.GET:meals.append('latenight');search_filters.append("meal: latenight")
		meals_pois=[]
		print "\ngood_for_meals:",meals
		if meals:
			for poi in pois:
				isOk=True
				for meal in meals:
					if poi['good_for_meal'][meal]!="True":
						isOk=False
				if isOk:
					meals_pois.append(poi)
			pois=meals_pois

		# FILTER POIS BY BUSINESS PARKING
		parkings=[]
		if 'parking-garage' in request.GET:parkings.append('garage');search_filters.append("parking: garage")
		if 'parking-lot' in request.GET:parkings.append('lot');search_filters.append("parking: lot")
		if 'parking-street' in request.GET:parkings.append('street');search_filters.append("parking: street")
		if 'parking-valet' in request.GET:parkings.append('valet');search_filters.append("parking: valet")
		if 'parking-validated' in request.GET:parkings.append('validated');search_filters.append("parking: validated")
		parkings_pois=[]
		print "\bbusiness_parking:",parkings
		if parkings:
			for poi in pois:
				isOk=True
				for parking in parkings:
					if poi['business_parking'][parking]!="True":
						isOk=False
				if isOk:
					parkings_pois.append(poi)
			pois=parkings_pois

		# FILTER POIS BY AMBIENCE
		ambiences=[]
		if'ambience-romantic' in request.GET:ambiences.append('romantic');search_filters.append("ambience: romantic")
		if'ambience-intimate' in request.GET:ambiences.append('intimate');search_filters.append("ambience: intimate")
		if'ambience-classy' in request.GET:ambiences.append('classy');search_filters.append("ambience: classy")
		if'ambience-hipster' in request.GET:ambiences.append('hipster');search_filters.append("ambience: hipster")
		if'ambience-divey' in request.GET:ambiences.append('divey');search_filters.append("ambience: divey")
		if'ambience-touristy' in request.GET:ambiences.append('touristy');search_filters.append("ambience: touristy")
		if'ambience-upscale' in request.GET:ambiences.append('upscale');search_filters.append("ambience: upscale")
		if'ambience-casual' in request.GET:ambiences.append('casual');search_filters.append("ambience: casual")
		ambiences_pois=[]
		print "\bambiences:",ambiences
		if ambiences:
			for poi in pois:
				isOk=True
				for ambience in ambiences:
					if poi['ambience'][ambience]!="True":
						isOk=False
				if isOk:
					ambiences_pois.append(poi)
			pois=ambiences_pois

		
		#FILTER POIS BY MUSIC
		musics=[]
		if 'music-dj' in request.GET:musics.append('dj');search_filters.append("ambience: dj")
		if 'music-background' in request.GET:musics.append('background');search_filters.append("ambience: background")
		if 'music-music' in request.GET:musics.append('music');search_filters.append("ambience: music")
		if 'music-karaoke' in request.GET:musics.append('karaoke');search_filters.append("ambience: karaoke")
		if 'music-live' in request.GET:musics.append('live');search_filters.append("ambience: live")
		if 'music-video' in request.GET:musics.append('video');search_filters.append("ambience: video")
		if 'music-jukebox' in request.GET:musics.append('jukebox');search_filters.append("ambience: jukebox")
		music_pois=[]
		print "\bmusics:",musics
		if musics:
			for poi in pois:
				isOk=True
				for music in musics:
					if poi['music'][music]!="True":
						isOk=False
				if isOk:
					music_pois.append(poi)
			pois=music_pois

		# GENERAL ATTRIBUTES
		general_attributes_pois=[]
		atleastOne=False
		for poi in pois:
			isOk=True
			if 'appointment-only' in request.GET: 
				atleastOne=True
				if "appointment-only" not in search_filters:
					search_filters.append("appointment-only")
				if poi['by_appointment_only']!='True':
					isOk=False
					continue
			if 'accepts-card' in request.GET:
				atleastOne=True
				if "accepts-card" not in search_filters:
					search_filters.append("accepts-card")
				if poi['business_accepts_credit_cards']!='True':
					isOk=False
					continue
			if 'accepts-bitcoin' in request.GET:
				atleastOne=True
				if "accepts-bitcoin" not in search_filters:
					search_filters.append("accepts-bitcoin")
				if poi['business_accepts_bitcoin']!='True':
					isOk=False
					continue
			if 'hasTv' in request.GET:
				atleastOne=True
				if "hasTv" not in search_filters:
					search_filters.append("hasTv")
				if poi['has_tv']!='True':
					isOk=False
					continue
			if 'hasWifi' in request.GET:
				atleastOne=True
				if "hasWifi" not in search_filters:
					search_filters.append("hasWifi")
				if poi['wifi']!='free':
					isOk=False
					continue
			if 'alcohol' in request.GET:
				atleastOne=True
				if "alcohol" not in search_filters:
					search_filters.append("alcohol")
				if poi['alcohol']!='full_bar' and poi['alcohol']!='beer_and_wine':
					isOk=False
					continue
			if 'happy-hour' in request.GET:
				atleastOne=True
				if "happy-hour" not in search_filters:
					search_filters.append("happy-hour")
				if poi['happyhour']!='True':
					isOk=False
					continue
			if 'good-for-dancing' in request.GET:
				atleastOne=True
				if "good-for-dancing" not in search_filters:
					search_filters.append("good-for-dancing")
				if poi['good_for_dancing']!='True':
					isOk=False
					continue
			if 'reservations' in request.GET:
				atleastOne=True
				if "reservations" not in search_filters:
					search_filters.append("reservations")
				if poi['restaurants_reservations']!='True':
					isOk=False
					continue
			if 'caters' in request.GET:
				atleastOne=True
				if "caters" not in search_filters:
					search_filters.append("caters")
				if poi['caters']!='True':
					isOk=False
					continue
			if 'take-out' in request.GET:
				atleastOne=True
				if "take-out" not in search_filters:
					search_filters.append("take-out")
				if poi['restaurants_takeout']!='True':
					isOk=False
					continue
			if 'good-for-groups' in request.GET:
				atleastOne=True
				if "good-for-groups" not in search_filters:
					search_filters.append("good-for-groups")
				if poi['restaurants_good_for_groups']!='True':
					isOk=False
					continue
			if 'delivery' in request.GET:
				atleastOne=True
				if "delivery" not in search_filters:
					search_filters.append("delivery")
				if poi['restaurants_delivery']!='True':
					isOk=False
					continue
			if 'drive-thru' in request.GET:
				atleastOne=True
				if "drive-thru" not in search_filters:
					search_filters.append("drive-thru")
				if poi['drivethru']!='True':
					isOk=False
					continue
			if 'outdoor-seating' in request.GET:
				atleastOne=True
				if "outdoor-seating" not in search_filters:
					search_filters.append("outdoor-seating")
				if poi['outdoorseating']!='True':
					isOk=False
					continue
			if 'bike-parking' in request.GET:
				atleastOne=True
				if "bike-parking" not in search_filters:
					search_filters.append("bike-parking")
				if poi['bikeparking']!='True':
					isOk=False
					continue
			if 'wheelchair' in request.GET:
				atleastOne=True
				if "wheelchair" not in search_filters:
					search_filters.append("wheelchair")
				if poi['wheelchair_accessible']!='True':
					isOk=False
					continue
			if 'dogs-allowed' in request.GET:
				atleastOne=True
				if "dogs-allowed" not in search_filters:
					search_filters.append("dogs-allowed")
				if poi['dogsallowed']!='True':
					isOk=False
					continue
			if 'good-for-kids' in request.GET:
				atleastOne=True
				if "good-for-kids" not in search_filters:
					search_filters.append("good-for-kids")
				if poi['goodforkids']!='True':
					isOk=False
					continue
			if isOk:
				general_attributes_pois.append(poi)
		
		if atleastOne:
			print "At least one!!!!"
			pois=general_attributes_pois
		else:
			print "pois hasn't change"
	
		# poi['restaurants_pricerange']

		context={'pois':pois,"search_filters":search_filters}
		return render(request, "results.html", context) # {}: context variables
	else:
		return HttpResponse("<h1>POST method is not supported</h1>",{})

def search(request):
	if request.method == "GET":
		if 'city' not in request.GET:
			print "SHOULD NEVER REACH THIS. city not in parameters"
			return HttpResponse("<h1>No city specified. No data to display!</h1>",{})

		query_str="select * from business_by_city where city='" + request.GET['city'] + "';"
		rowRes=session.execute(query_str);
		pois=[]
		all_categories=[]
		businessids=[]
		for row in rowRes:
			# Name
			pois.append({'name':row.name})
			# print "pois[current]=",pois[len(pois)-1]['name']
			# Categories
			pois[len(pois)-1]['categories']=[]
			if row.categories:
				for category in row.categories:
					pois[len(pois)-1]['categories'].append(str(category))
					if category not in all_categories:
						all_categories.append(str(category))
			# Hours
			hours=[]
			hours.append(('Mon',row.hours['Monday']))
			hours.append(('Tue',row.hours['Tuesday']))
			hours.append(('Wed',row.hours['Wednesday']))
			hours.append(('Thu',row.hours['Thursday']))
			hours.append(('Fri',row.hours['Friday']))
			hours.append(('Sat',row.hours['Saturday']))
			hours.append(('Sun',row.hours['Sunday']))
			pois[len(pois)-1]['hours']=hours
			# Stars
			pois[len(pois)-1]['stars']=row.stars
			pois[len(pois)-1]['review_count']=row.review_count
			# BUSINESSID
			pois[len(pois)-1]['businessid']=row.businessid
			businessids.append(row.businessid)
			# print hours
			# print "stars:", pois[len(pois)-1]['stars']
			# print "businessid:", pois[len(pois)-1]['businessid']
		context={'city':request.GET['city'], 'categories':all_categories, 'pois':pois, 'businessids':businessids}
		return render(request, "search.html", context) # {}: context variables
	else:
		return HttpResponse("<h1>POST method is not supported</h1>",{})

def business(request):
	if request.method == "GET":
		if 'businessid' not in request.GET:
			print "SHOULD NEVER REACH THIS. city not in parameters"
			return HttpResponse("<h1>No business specified. No data to display!</h1>",{})
		print request.GET['businessid']
		query_str="select * from business_by_id where businessid='" + request.GET['businessid'] + "';"
		rowRes=session.execute(query_str);
		poi={}
		for row in rowRes:
			poi['businessid']=row.businessid
			poi['name']=row.name
			poi['address']=row.address
			poi['postal_code']=row.postal_code
			poi['city']=row.city
			poi['state']=row.state
			poi['latitude']=row.coordinates['latitude']
			poi['longtitude']=row.coordinates['longtitude']
			poi['review_count']=row.review_count

			# Categories
			poi['categories']=[]
			if row.categories:
				for category in row.categories:
					poi['categories'].append(str(category))
			# Hours
			hours=[]
			hours.append(('Mon',row.hours['Monday']))
			hours.append(('Tue',row.hours['Tuesday']))
			hours.append(('Wed',row.hours['Wednesday']))
			hours.append(('Thu',row.hours['Thursday']))
			hours.append(('Fri',row.hours['Friday']))
			hours.append(('Sat',row.hours['Saturday']))
			hours.append(('Sun',row.hours['Sunday']))
			poi['hours']=hours
			poi['stars']=row.stars
			poi['good_for_meal']=row.good_for_meal
			poi['business_parking']=row.business_parking
			poi['ambience']=row.ambience
			poi['music']=row.ambience

			general_attributes=row.general_attributes
			poi['noiselevel']=general_attributes['noiselevel']
			# GENERAL ATTRIBUTES
			general_attr=[]
			general_attr.append(('Accepts Credit Cards',general_attributes['business_accepts_credit_cards']))
			general_attr.append(('Accepts Bitcoin',general_attributes['business_accepts_bitcoin']))
			general_attr.append(('By appointment only',general_attributes['by_appointment_only']))
			general_attr.append(('TV',general_attributes['has_tv']))
			general_attr.append(('Wifi',general_attributes['wifi']))
			general_attr.append(('Alcohol',general_attributes['alcohol']))
			general_attr.append(('Happy hour',general_attributes['happyhour']))
			general_attr.append(('Bike parking',general_attributes['bikeparking']))
			general_attr.append(('Caters',general_attributes['caters']))
			general_attr.append(('Drive Thru',general_attributes['drivethru']))
			general_attr.append(('Outdoor seating',general_attributes['outdoorseating']))
			general_attr.append(('Delivery',general_attributes['restaurants_delivery']))
			general_attr.append(('Good for groups',general_attributes['restaurants_good_for_groups']))
			general_attr.append(('Pricerange (max:3)',general_attributes['restaurants_pricerange']))
			general_attr.append(('Reservations',general_attributes['restaurants_reservations']))
			general_attr.append(('Takeout',general_attributes['restaurants_takeout']))
			general_attr.append(('Wheelchair Accessible',general_attributes['wheelchair_accessible']))
			general_attr.append(('Dogs allowed',general_attributes['dogsallowed']))
			general_attr.append(('Good for kids',general_attributes['goodforkids']))
			general_attr.append(('Good for dancing',general_attributes['good_for_dancing']))
			poi['general_attributes']=general_attr
			break
		
		query_str="select * from review_by_businessid where businessid='" + request.GET['businessid'] + "';"
		rowRes=session.execute(query_str);
		reviews=[]
		star_sum=0
		for row in rowRes:
			review={}
			review['date']=row.date
			review['stars']=row.stars
			# print row.stars
			star_sum+=row.stars
			review['review']=row.review
			review['userid']=row.userid
			# print "The userid: ", row.userid
			query_str="select * from user where userid='" + row.userid + "';"
			rowRes_user=session.execute(query_str);
			if not rowRes_user:
				pass
				# print "User not found!!"
			else:
				for row_user in rowRes_user:
					pass
					# print "user's name: ", row_user.name
			review['username']=row_user.name
			reviews.append(review)
			# print "\n\n"
		poi['stars']=0.5*round(star_sum/float(len(reviews))/0.5)
		session.execute("update business_by_id set stars="+ str(poi['stars']) +" where businessid='"+request.GET['businessid']+"';")
		session.execute("update business_by_city set stars="+ str(poi['stars']) +" where businessid='"+request.GET['businessid']+"' and city='"+poi['city']+"';")
		review_count=len(reviews)
		# change review_count & stars here
		query_str="select * from tip_by_businessid where businessid='" + request.GET['businessid'] + "';"
		rowRes=session.execute(query_str);
		tips=[]
		star_sum=0
		for row in rowRes:
			tip={}
			tip['date']=row.date
			tip['tip']=row.tip
			tip['userid']=row.userid
			query_str="select * from user where userid='" + row.userid + "';"
			rowRes_user=session.execute(query_str);
			if not rowRes_user:
				pass
				# print "User not found!!"
			else:
				for row_user in rowRes_user:
					pass
					# print "user's name: ", row_user.name
			tip['username']=row_user.name
			tips.append(tip)
			# print "\n\n"
		tip_count=len(tips)
		context={'poi':poi, 'reviews':reviews, 'tips':tips, 'review_count':review_count, 'tip_count':tip_count}
		return render(request, "business.html", context) # {}: context variables
	else:
		return HttpResponse("<h1>POST method is not supported</h1>",{})

def insert_review(request):
	if request.method=="GET":
		if 'businessid' not in request.GET or 'userid'not in request.GET or 'username'not in request.GET or 'review'not in request.GET or 'stars'not in request.GET:
			print "SHOULD NEVER REACH THIS. not enough parameters"
			return HttpResponse("<h1>No data to display!</h1>",{}) 
		businessid=request.GET.get('businessid')
		userid=request.GET.get('userid')
		username=request.GET.get('username')
		review=request.GET.get('review').replace("'", "''")
		stars=float(request.GET.get('stars'))
		city=request.GET.get('city')
		if 'checkIfExists' in request.GET:
			checkIfExists=True
		else:
			checkIfExists=False

		# Check if user in db -> create if not
		successfulInsert=False
		createUser=False
		query_str="select * from user where userid='" + userid + "';"
		rowRes=session.execute(query_str);
		if not rowRes:
			print("User doesn't exist.")
			if checkIfExists: # an den uparxei o xrhsths kai thelw na dhmiourghsw
				# insert user
				query_str="insert into user(userid, average_stars,fans, name, review_count) values('"+userid+"',"+str(stars)+","+str(0)+",'"+username+"', "+str(1)+");"
				print query_str
				session.execute(query_str) 
				# epanalhptika mexri na breis ena review id pou na mhn uparxei mesa
				reviewid=0
				while True:
					query_str="select * from review_by_businessid where businessid='"+businessid+"' and reviewid='"+str(reviewid)+"';"
					if not session.execute(query_str):
						print("NO REVIEW FOUND WITH reviewid:", reviewid)
						break
					reviewid+=1
				date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
				# insert review
				query_str="insert into review_by_businessid(businessid, reviewid,date, review, stars, userid) values('"+businessid+"','"+str(reviewid)+"','"+date+"','"+review+"',"+str(stars)+",'"+userid+"');"
				print query_str
				session.execute(query_str)
				query_str="insert into review_by_userid(businessid, reviewid,date, review, stars, userid) values('"+businessid+"','"+str(reviewid)+"','"+date+"','"+review+"',"+str(stars)+",'"+userid+"');"
				session.execute(query_str)
				
				successfulInsert=True
				rowRes_bus=session.execute("select review_count, stars from business_by_id where businessid='"+businessid+"';")
				for row_bus in rowRes_bus:
					session.execute("update business_by_id set review_count="+ str(row_bus.review_count+1) +" where businessid='"+businessid+"';")
					session.execute("update business_by_city set review_count="+ str(row_bus.review_count+1) +" where businessid='"+businessid+"' and city='"+city+"';")
					session.execute("update business_by_id set stars="+ str((row_bus.stars+stars)/2) +" where businessid='"+businessid+"';")
					session.execute("update business_by_city set stars="+ str((row_bus.stars+stars)/2) +" where businessid='"+businessid+"' and city='"+city+"';")
					break
				createUser=True
			else:
				print("Not going to add user. Not going to add review")
		else:
			for row in rowRes:
				pass
			row.review_count
			session.execute("update user set review_count="+str(row.review_count+1)+" where userid='"+userid+"';")
			# epanalhptika mexri na breis ena review id pou na mhn uparxei mesa
			reviewid=0
			while True:
				query_str="select * from review_by_businessid where businessid='"+businessid+"' and reviewid='"+str(reviewid)+"';"
				if not session.execute(query_str):
					print("NO REVIEW FOUND WITH reviewid:", reviewid)
					break
				reviewid+=1
			date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
			# insert review
			query_str="insert into review_by_businessid(businessid, reviewid,date, review, stars, userid) values('"+businessid+"','"+str(reviewid)+"','"+date+"','"+review+"',"+str(stars)+",'"+userid+"');"
			print query_str
			session.execute(query_str)
			query_str="insert into review_by_userid(businessid, reviewid,date, review, stars, userid) values('"+businessid+"','"+str(reviewid)+"','"+date+"','"+review+"',"+str(stars)+",'"+userid+"');"
			session.execute(query_str)

			rowRes_bus=session.execute("select review_count, stars from business_by_id where businessid='"+businessid+"';")
			for row_bus in rowRes_bus:
				session.execute("update business_by_id set review_count="+ str(row_bus.review_count+1) +" where businessid='"+businessid+"';")
				session.execute("update business_by_city set review_count="+ str(row_bus.review_count+1) +" where businessid='"+businessid+"' and city='"+city+"';")
				session.execute("update business_by_id set stars="+ str((row_bus.stars+stars)/2) +" where businessid='"+businessid+"';")
				session.execute("update business_by_city set stars="+ str((row_bus.stars+stars)/2) +" where businessid='"+businessid+"' and city='"+city+"';")
				break
			successfulInsert=True

		context={'successfulInsert':successfulInsert, 'createUser':createUser, 'userid':userid, "username":username, "review":review, "stars":stars, 'businessid':businessid}
		return render(request, "review.html", context)
	else:
		return HttpResponse("<h1>POST method is not supported</h1>",{})

def insert_tip(request):
	if request.method=="GET":
		if 'businessid' not in request.GET or 'userid'not in request.GET or 'username'not in request.GET or 'tip'not in request.GET:
			print "SHOULD NEVER REACH THIS. not enough parameters"
			return HttpResponse("<h1>No data to display!</h1>",{}) 
		businessid=request.GET.get('businessid')
		userid=request.GET.get('userid')
		username=request.GET.get('username')
		tip=request.GET.get('tip').replace("'", "''")
		city=request.GET.get('city')
		if 'checkIfExists' in request.GET:
			checkIfExists=True
		else:
			checkIfExists=False

		# Check if user in db -> create if not
		successfulInsert=False
		createUser=False
		query_str="select * from user where userid='" + userid + "';"
		rowRes=session.execute(query_str);
		if not rowRes:
			print("User doesn't exist.")
			if checkIfExists: # an den uparxei o xrhsths kai thelw na dhmiourghsw
				# insert user 
				query_str="insert into user(userid, average_stars,fans, name, review_count) values('"+userid+"',"+str(0)+","+str(0)+",'"+username+"', "+str(0)+");"
				print(query_str)
				session.execute(query_str)
				date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
				# insert tip
				query_str="insert into tip_by_businessid(businessid,date, tip, userid) values('"+businessid+"','"+date+"','"+tip+"','"+userid+"');"
				print query_str
				session.execute(query_str)
				query_str="insert into tip_by_userid(businessid,date, tip, userid) values('"+businessid+"','"+date+"','"+tip+"','"+userid+"');"
				session.execute(query_str)
				successfulInsert=True
				createUser=True
			else:
				print("Not going to add user. Not going to add tip")
		else:
			date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
			# insert tip
			query_str="insert into tip_by_businessid(businessid,date, tip, userid) values('"+businessid+"','"+date+"','"+tip+"','"+userid+"');"
			print query_str
			session.execute(query_str)
			query_str="insert into tip_by_userid(businessid,date, tip, userid) values('"+businessid+"','"+date+"','"+tip+"','"+userid+"');"
			session.execute(query_str)
			successfulInsert=True

		context={'successfulInsert':successfulInsert, 'createUser':createUser, 'userid':userid, "username":username, "tip":tip, 'businessid':businessid}
		return render(request, "tip.html", context)
	else:
		return HttpResponse("<h1>POST method is not supported</h1>",{})

def user(request):
	if request.method=="GET":
		if 'userid' not in request.GET:
			print "SHOULD NEVER REACH THIS. not enough parameters"
			return HttpResponse("<h1>No data to display!</h1>",{}) 

		# Get all info from user table
		userid=request.GET['userid']
		query_str="select * from user where userid='" + userid + "';"
		rowRes_user=session.execute(query_str);
		if rowRes_user:
			for row_user in rowRes_user:pass
		user={}
		user['name']=row_user.name
		# user['average_stars']=row_user.average_stars
		user['review_count']=row_user.review_count
		
		# Get all reviews and tips of this user
		reviews=[]
		query_str="select * from review_by_userid where userid='" + userid + "';"
		rowRes=session.execute(query_str);
		star_sum=0
		for row in rowRes:
			review={}
			review['date']=row.date
			review['stars']=row.stars
			star_sum+=row.stars
			review['review']=row.review
			query_str="select * from business_by_id where businessid='" + row.businessid + "';"
			rowRes_bussiness=session.execute(query_str);
			if rowRes_bussiness:
				for row_business in rowRes_bussiness:
					pass
			review['business_name']=row_business.name
			reviews.append(review)
		user['average_stars']=star_sum/float(len(reviews))

		tips=[]
		query_str="select * from tip_by_userid where userid='" + userid + "';"
		rowRes=session.execute(query_str);
		for row in rowRes:
			tip={}
			tip['date']=row.date
			tip['tip']=row.tip
			query_str="select * from business_by_id where businessid='" + row.businessid + "';"
			rowRes_bussiness=session.execute(query_str);
			if rowRes_bussiness:
				for row_business in rowRes_bussiness:pass
			tip['business_name']=row_business.name
			tips.append(tip)
		context={'user':user, 'reviews':reviews, 'tips':tips}
		return render(request, "user.html", context)
	else:
		return HttpResponse("<h1>POST method is not supported</h1>",{})