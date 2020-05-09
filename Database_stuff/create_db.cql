TO CREATE KEYSPACE recommedations_keyspace:
create keyspace recommedations_keyspace with replication={'class':'SimpleStrategy', 'replication_factor':1};
----------------------------------------------------------------
TO CREATE TABLES tip:

create table tip_by_businessid(
businessid text, 
userid text, 
date text, 
tip text,
primary key(businessid, userid, date));

create table tip_by_userid(
businessid text, 
userid text, 
date text, 
tip text,
primary key(userid, businessid, date));


1222917 eggrafes
----------------------------------------------------------------
TO CREATE TABLE user:

create table user(
userid text, 
name text, 
review_count int, 
fans int, 
average_stars float,
primary key(userid));

1637138 eggrafes
----------------------------------------------------------------
TO CREATE TABLES review

create table review_by_businessid(
businessid text, 
reviewid text, 
userid text, 
date text, 
stars float, 
review text,
primary key(businessid, reviewid));

create table review_by_userid(
businessid text, 
reviewid text, 
userid text, 
date text, 
stars float, 
review text,
primary key(userid, reviewid));

21719139 eggrafes
----------------------------------------------------------------
TO CREATE TABLE business

create table business_by_id(
businessid text,
name text,
address text,
city text,
state text,
postal_code text,
coordinates map<text, double>,
stars float,
review_count int,
categories set<text>,
hours map<text,text>,
general_attributes map<text,text>,
good_for_meal map<text,text>,
business_parking map<text,text>,
ambience map<text,text>,
music map<text,text>,
primary key(businessid));

create table business_by_city(
businessid text,
name text,
address text,
city text,
state text,
postal_code text,
coordinates map<text, double>,
stars float,
review_count int,
categories set<text>,
hours map<text,text>,
general_attributes map<text,text>,
good_for_meal map<text,text>,
business_parking map<text,text>,
ambience map<text,text>,
music map<text,text>,
primary key(city, businessid));


192608 eggrafes