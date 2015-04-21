import logging
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

    def get_search_id(self,user_id):
        '''
        This method returns the search id generated by CD

        Chief Delphi redirects seraches to another page and it is necessary to know what page.
        This function returns the page id as a string rather than an int
        '''
        page_file = "search.php"
        params_payload = {"do":"finduser","u":user_id }
        page = requests.get(url_base + page_file, params=params_payload)
        urlString = page.url
        print(urlString)
        return urlString[urlString.find("searchid")+9:]

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
        numPosts = soup.find_all('table',  attrs={'class':'tborder'})[3].find_all("tr")[1].find_all('td')[0].find_all('div', attrs={'class':'fieldset'})[1]
        print(numPosts)

    def get_all_posts(self, user_id):
        '''
        this method returns a list of all the posts by the specified user

        :param int user_id: The user id
        :return list[string]: Post data. Each post is a different element
        '''
        post_data = []
        page_file = "search.php"
        params_payload = {"do":"finduser","u":user_id }
        soup = self.get_page(page_file,params_payload)
        #logging.debug(soup)
        num_pages_string = soup.find_all('td', attrs={'class':'vbmenu_control'})[10].text
        num_pages = int(num_pages_string[num_pages_string.find('of')+3])
        s_id = self.get_search_id(user_id)
        for curr_page in range(1,num_pages):
            params_payload = {"searchid":s_id, "page":curr_page}
            search_soup = self.get_page(page_file,params_payload)
            form = search_soup.find_all("form", {"id":"inlinemodform", "method":"post"})[0]
            posts = form.find_all("table")
            junkTables = [0,len(posts) - 1,len(posts) - 2, len(posts) - 3]
            i = 0
            for post in posts:
                if i in junkTables:
                    continue
                    #there are 4 junk tables that we can skip over
                post_data.append(post.find_all("em")[0].text)
                i+=1
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
        
    