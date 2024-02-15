import bs4
from bs4 import BeautifulSoup


def parserv2(soup : BeautifulSoup):
    items : bs4.ResultSet = soup.find_all('a',string= ["1"],  href=True )
    for item in items:
        print( item['href'] )
    pass