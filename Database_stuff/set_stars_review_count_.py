""" Olympia Axelou, May 2020
 This script is part of the project "A POI search engine using CassandraDB"
 
 It's used to set stars and review_count correctly, as there was a difference
 between business.json & review.json

"""
from cassandra.cluster import Cluster
import cassandra 

cluster = Cluster()
session = cluster.connect('recommendations_keyspace')

query_str="select businessid, city, stars from business_by_id;"
rowRes=session.execute(query_str);
for row in rowRes:
	counted_stars=0.0
	counted_reviews=0
	query_str="select stars from review_by_businessid where businessid='" + row.businessid + "';"
	rowRes_review=session.execute(query_str);
	for row_review in rowRes_review:
		counted_stars+=row_review.stars
		counted_reviews+=1
	if counted_reviews>0:
		counted_stars=counted_stars/float(counted_reviews)
	else:
		counted_stars=0
	# print row.businessid, ":", str(row.stars), "vs", str(0.5*round(counted_stars/0.5))
	try:
		if row.stars != (0.5*round(counted_stars/0.5)):
			session.execute("update business_by_id set stars="+str(0.5*round(counted_stars/0.5))+" where businessid='"+row.businessid+"';")
			session.execute("update business_by_city set stars="+str(0.5*round(counted_stars/0.5))+" where city='"+row.city+"' and businessid='"+row.businessid+"';")
		session.execute("update business_by_id set review_count="+str(counted_reviews)+" where businessid='"+row.businessid+"';")
		session.execute("update business_by_city set review_count="+str(counted_reviews)+" where city='"+row.city+"' and businessid='"+row.businessid+"';")
	except cassandra.protocol.SyntaxException as e:
		print "Going to ignore", row.businessid, "from", row.city

