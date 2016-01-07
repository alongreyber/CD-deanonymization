from chiefdelphi_scraper import ChiefDelphi
import hashlib
import string

class JGAAPInterface(object):
	def by_author_dedup(self,posts):
		'''
		takes in a database and deduplicates posts and then creates a dictionary of name and all text by that user.
		'''
		db = {}
		used_lines = []
		posts_done = 0
		print("deduplicating all posts")
		for post in posts:
			for line in post['text']:
				if "Originally by" not in line:
					line_ascii = line.encode('ascii', 'ignore')
					hashed_line = hashlib.md5(line_ascii).hexdigest()
					if hashed_line not in used_lines: #if the line has been used in any previous post
						used_lines.append(hashed_line)
					else:
						username = post['name']
						if username in db:
							db[post['name']] += line
						else:
							db[post['name']] = line
			posts_done += 1
			print("deduplicated " + str(posts_done) + " of " + str(len(posts)))
			print(str(len(used_lines)) + "unique lines so far")
		return db

	def write_to_files(self,db,min_characters):
		'''
		writes from the output of by_author_dedup to a file naming convention accpeted by jgaap
		'''
		corpus_file = open('corpus.txt','w')
		print("writing files to disk")
		for author in db:
			author_file_name = "posts_" + author + ".txt"
			valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
			author_file_name = ''.join(c for c in author_file_name if c in valid_chars)
			write_text = ''.join(c for c in db[author] if c in valid_chars) #remove invalid characters from text
			#an average paragraph is 125 words long with average characters/word being 5.1 = 637.5 characters/paragraph
			if len(write_text) > min_characters:
				f = open(author_file_name,'w')
				f.write(write_text)
				corpus_file.write(author + "," + author_file_name + "\n")
				f.close()
		corpus_file.close()
