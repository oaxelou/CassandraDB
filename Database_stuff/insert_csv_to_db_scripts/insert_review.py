from cassandra.cluster import Cluster
import csv
import time, datetime

cluster = Cluster()
session = cluster.connect('recommedations_keyspace')

with open('review.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count=0
	for row in csv_reader:
		if line_count>0 and row[0] and row[1] and row[2] and row[3]:
			reviewid=row[0]
			userid=row[1]
			businessid=row[2]
			stars=row[3]
			review=row[4].replace("'", "''")
			date=row[5]
			query_str="insert into review_by_businessid(businessid, reviewid, userid, date, stars, review) values('"+row[2]+"','"+row[0]+"','"+row[1]+"','"+row[5]+"',"+row[3]+",'"  +row[4].replace("'", "''")+"');"
			session.execute(query_str);
			query_str="insert into review_by_userid(businessid, reviewid, userid, date, stars, review) values('"+row[2]+"','"+row[0]+"','"+row[1]+"','"+row[5]+"',"+row[3]+",'"  +row[4].replace("'", "''")+"');"
			session.execute(query_str);
		else:
			print line_count, "The primary key should not be null. This row is omitted"
			print row
		if line_count % 10000 == 0:
			print str(line_count) + " " + str(datetime.datetime.now().strftime("%H:%M:%S"))
		line_count+=1
	print "Processed ", line_count, " lines."

print "finished"	