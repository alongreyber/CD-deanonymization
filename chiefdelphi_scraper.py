import logging
import requests
from bs4 import BeautifulSoup

url_base = "http://chiefdelphi.com/forums/"

target_user_id = 25240



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
        numPosts = soup.find_all('table',  attrs={'class':'tborder'})[3].find_all("tr")[1].find_all('td')[0].find_all('div', attrs={'class':'fieldset'})[1]
        print(numPosts)

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
        
    