from chiefdelphi_scraper import ChiefDelphi
import hashlib

class JGAAPInterface(object):

	def __init__(self):

	def by_author_dedup(self,posts):
		'''
		takes in a database and deduplicates posts and then creates a dictionary of name and all text by that user.
		'''
		db = {}
		used_lines = []
		for post in posts:
			for line in post['text']:
				if "Originally by" not in line:
					hashed_line = hashlib.md5(line).hexdigest()
					if hashed_line not in used_lines: #if the line has been used in any previous post
						used_lines.append(hashed_line)
					else:
						username = post['name']
						if username in db:
							db[post['name']] += line
						else:
							db[post['name']] = line
		return db
