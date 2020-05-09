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
			name=row[1].replace("'", "''")
			review_count=int(float(row[2]))
			fans=int(float(row[3]))
			average_stars=float(row[4])
			query_str="insert into user(userid, name, review_count, fans, average_stars) values('"+str(userid)+"','"+str(name)+"',"+str(review_count)+","+str(fans)+","+str(average_stars)+");"
			session.execute(query_str);
		if line_count % 10000 == 0:
			print str(line_count) + " " + str(datetime.datetime.now().strftime("%H:%M:%S"))
		line_count+=1
	print "Processed ", line_count, " lines."

print "finished"	