import logging
import re
import requests
from bs4 import BeautifulSoup

url_base = "http://chiefdelphi.com/forums/"
target_user_id = 25240;


class ChiefDelphi (object):
    '''
    This is the ChiefDelphi Object. It does things with ChiefDelphi.
    '''
    def __init__(self, log_level=logging.DEBUG):
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
        join_date = soup.find_all('table',  attrs={'class':'tborder'})[3].find_all("tr")[1].find_all('td')[0].find('div', attrs={'class':'fieldset'}).text.strip()
        logging.debug("Found join date of:%s for id: %s" % (join_date, user_id))
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

    def get_all_posts(self, user_id):
        '''
        This method returns a list of all the posts by the specified user

        :param int user_id: The user id
        :return list[string]: Post data. Each post is a different element
        '''
        post_data = []
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
            post_data.append(post)
        return post_data

def main():
    '''
    This is a pretty little main method
    '''
    cd = ChiefDelphi()
    cd.get_user_name(target_user_id)
    cd.get_user_join_date(target_user_id)

if __name__ == "__main__":
    '''
    This executes if the script gets called. Useful for quick and dirty testing
    '''
    main()
        
    