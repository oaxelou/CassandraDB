from cassandra.cluster import Cluster
import csv
import time, datetime

cluster = Cluster()
session = cluster.connect('recommedations_keyspace')

with open('tip.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count=0
	for row in csv_reader:
		if line_count>0 and row[0] and row[1] and row[3]:
			userid=row[0]
			businessid=row[1]
			text=row[2].replace("'", "''")
			date=row[3]
			query_str="insert into tip_by_businessid(businessid, userid, tip, date) values('"+businessid+"','"+userid+"','"+text+"','"+date+"');"
			session.execute(query_str);
			query_str="insert into tip_by_userid(businessid, userid, tip, date) values('"+businessid+"','"+userid+"','"+text+"','"+date+"');"
			session.execute(query_str);
		if line_count % 10000 == 0:
			print str(line_count) + " " + str(datetime.datetime.now().strftime("%H:%M:%S"))
		line_count+=1
	print "Processed ", line_count, " lines."

print "finished"	