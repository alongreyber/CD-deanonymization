import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime

url_base = "http://chiefdelphi.com/forums/"
target_user_id = 25240;

#small functions that make it easier to save and load the tables of data that we're working with
def save_table(table,name):
    pickle.dump(table,open(name + ".pikl","wb"))
def load_table(name):
    return pickle.load(open(name + ".pikl","rb"))

class ChiefDelphi (object):
    '''
    This is the ChiefDelphi Object. It does things with ChiefDelphi.
    '''
    def __init__(self, log_level=logging.CRITICAL):
        self.logger = logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

    def get_page(self, page_php, params):
        '''
        returns beautiful soup content

        
        '''
        user_page = requests.get(url_base + page_php, params=params)
        user_page.raise_for_status()
        soup = BeautifulSoup(user_page.content)
        return soup

    def get_user_name(self, user_id):
        '''
        This method gets a join date for a given user id
        
        :param int user_id: The user id to find the date of
        :return string: The date a user joined
        '''
        params_payload = {"u": user_id}
        page_file = "member.php"
        soup = self.get_page(page_file, params_payload)
        logging.debug(soup)
        user_name = soup.find('table',  attrs={'class':'tborder'}).find_all("tr")[0].find_all('tr')[1].find_all('td')[0].text.strip()
        logging.debug("Found username: %s for id: %s" % (user_name, user_id))
        return user_name

    def get_user_join_date(self, user_id):
        '''
        This method gets a join date for a given user id
        
        :param int user_id: The user id to find the date of
        :return datetime.date: The date a user joined
        '''
        params_payload = {"u": user_id}
        page_file = "member.php"
        soup = self.get_page(page_file, params_payload)
        logging.debug(soup)
        num_tables = len(soup.find_all('table',  attrs={'class':'tborder'})) #this helps if there is a signature on the page
        join_date_string = soup.find_all('table',  attrs={'class':'tborder'})[num_tables - 1].find_all("tr")[1].find_all('td')[0].find('div', attrs={'class':'fieldset'}).text.strip()
        yr = join_date_string[join_date_string.find("-") + 4:]
        mon = join_date_string[join_date_string.find("-") - 2:join_date_string.find("-")]
        day = join_date_string[join_date_string.find("-") + 1:join_date_string.find("-") + 3]
        join_date = date(int(yr),int(mon),int(day))
        logging.debug("Found join date of:%s for id: %s" % (join_date_string, user_id))
        return join_date

    def get_number_posts(self, user_id):
        '''
        This method gets the number of posts for a given user id

        :param int user_id: The user id
        :return int: Number of posts a user has made
        '''
        params_payload = {"u": user_id}
        page_file = "member.php"
        soup = self.get_page(page_file, params_payload)
        logging.debug(soup)
        numPosts = soup.find_all('table',  attrs={'class':'tborder'})[3].find("tr", attrs={"valign":"top"}).find('table').find('strong').text
        return int(numPosts)

    def valid_user(self,user_id):
        name = self.get_user_name(user_id) #I'm cheating and not writing a real function
        if name == 'vBulletin Message': #this is what happens when get_user_name is called for an invalid user
            return False
        else:
            return True

    def get_all_posts_by_user(self, user_id):
        '''
        This method returns a list of all the posts by the specified user

        :param int user_id: The user id
        '''
        post_list = []
        page_file = "search.php"
        params_payload = {"do":"finduser","u":user_id }
        search_session = requests.Session() #create a session
        num_posts = self.get_number_posts(user_id)
        initial_req = search_session.get(url_base + page_file, params=params_payload) #run the search
        initial_req.raise_for_status()
        new_params = "&page=1" + "&pp=" + str(num_posts)
        new_url = initial_req.url + new_params #create a new url that shows all posts on a single page
        page = search_session.get(new_url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content)
        logging.debug(soup)
        link_tags = soup.find_all("a", {"href":re.compile("showthread.*#post.*")}) #uses a regular expression to search for links to the posts
        for link_tag in link_tags:
            if link_tag == link_tags[0]: #the first link is really weird and isn't real
                continue
            link = link_tag['href']
            post_number = link[link.find("#post") + 5:]
            post_page_soup = self.get_page(link,{}) #this is the page of the forum with the full post on it
            logging.debug(post_page_soup)
            post = post_page_soup.find("div", {"id":"post_message_" + post_number})
            post_data = {post_number:post}
            post_list.append(post_data) 
        return post_list

    def get_user_data(self,min_posts):
        '''
        This method returns a list of all user ids with the specified number of posts

        '''
        return_list = []
        page_file = "memberlist.php"
        page_number = 1
        done = False
        while True:
            params_payload = {"order":"DESC","sort":"posts","pp":"100","page":str(page_number)}
            soup = self.get_page(page_file,params_payload)
            main_table = soup.find_all("form")[1].find_all("table")[1].find_all("tr",{"align":"center"})
            for row in main_table:
                if row == main_table[0]: #first row is just a header for the table
                    continue
                post_number_string = row.find_all("td")[1].text
                post_number = int(post_number_string.replace(',','')) #run a replace because the post number has commas
                if(post_number < min_posts):
                    done = True
                    break

                user_link_string = row.find("td").find("a")['href']
                user_id_string = user_link_string[user_link_string.find("u=")+2:]
                user_id = int(user_id_string)

                user_name = row.find("td").find("a").text
                team_number = row.find_all("td")[4].text
                join_date = self.get_user_join_date(user_id)

                user_data = {"name":user_name,"id":user_id,"posts":post_number,"join":join_date,"team":team_number}
                return_list.append(user_data)
            if done:
                break
            page_number += 1
        return return_list

    def str_to_date(self,date_string):
        '''
        parses string with format "MM-DD-YYYY, HH:MM AM/PM" into a datetime object
        '''
        mon = int(date_string[:2])
        day = int(date_string[3:5])
        yr = int(date_string[6:10])
        minute = int(date_string[15:17])

        hr = date_string[12:14]
        if date_string[18:20] == "PM":
            hr_int = (int(hr)+12) % 24 #mod 24 because chiefdelphi displays 1-24 and python accepts 0-23
        else:
            hr_int = int(hr)
        return datetime(yr,mon,day,hr_int,minute)
    
    def number_posts(self):
        '''
        Returns the number of pages of posts on chiefdelphi currently.
        Right now this number is in the range of 130,000
        '''
        acv_base = "archive/index.php/t-"
        cur_page = 137200
        while True:
            soup = self.get_page(acv_base+str(cur_page)+".html",{})
            if soup.find() == None: #the page is empty
                break
            else:
                cur_page += 1
        return cur_page-1

    def get_all_posts(self):
        '''
        Gets every post on chief delphi using the archive to increase speed
        This function still probably takes a while

        return format:

        returns a list of dictionaries. This allows relatively easy indexing.
        each element in the list is a post
        post can be indexed using keywords text,date,name
        '''
        return_data = []
        cur_post = 5
        cur_thousand_post = 0
        acv_base = "archive/index.php/t-"
        done = False
        iterate_threshold = 5
        no_post_count = 0
        while True: #this iterates for each 10,000 pages (corresponds almost perfectly to each year)
            while True:
                soup = self.get_page(acv_base+str(cur_post)+".html",{})
                posts = soup.find_all("div",{"class":"post"})
                if posts == None: #if nothing on the page 
                    no_post_count += 1 #this makes sure that we continue even after passing a blank page
                    if no_post_count >= iterate_threshold:
                        no_post_count = 0
                        break
                print("getting page " + str(cur_post))
                for post in posts:
                    user_name = post.find("div",{"class":"username"}).text
                    post_date_string = post.find("div",{"class":"date"}).text
                    post_date = self.str_to_date(post_date_string)
                    post_text = post.find("div",{"class":"posttext"})
                    post_data = {"text":post_text,"date":post_date,"name":user_name}
                    return_data.append(post_data)
                cur_post += 1
            cur_thousand_post += 1
            cur_post = cur_thousand_post * 10000
            if(cur_post >= 160000): #if the year is 2017 it's probably the end
                break
        return return_data







def main():
    '''
    This is a pretty little main method
    '''
    cd = ChiefDelphi()
    cd.get_all_posts()

if __name__ == "__main__":
    '''
    This executes if the script gets called. Useful for quick and dirty testing
    '''
    main()
        
    