import sqlite3
from chiefdelphi_scraper import ChiefDelphi

class DataBase(object):

	def __init__(self, cd_in, sq_db_in):
		self.cd = cd_in
		self.db_conn = sqlite3.connect(sq_db_in)
		self.db = db_conn.cursor()

		self.query("CREATE TABLE userdata (" \
		"id INTEGER," \
		"name TEXT," \
		"posts INTEGER,"\
		"joindate DATE," \
		"teamnumber INTEGER)")

		self.query("CREATE TABLE postdata (" \
		"postnum INTEGER," \
		"post TEXT)")


	def query(self,query_str):
		return self.db.execute(query_str)

	def populateData(min_posts):
		data = self.cd.get_user_data(min_posts)
