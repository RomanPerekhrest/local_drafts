from bs4 import BeautifulSoup
from datetime import datetime

with open('sort_html_by_date_input.html') as html_doc:
    soup = BeautifulSoup(html_doc, 'lxml')
    divs = {}
    
    for div in soup.find_all('div', 'date'):
        divs[datetime.strptime(div.string, '%a %B %d %Y')] = \
			str(div) + '\n' + div.find_next_sibling('ul').prettify()

    soup.body.clear()
    
    for el in sorted(divs, reverse=True):
        soup.body.append(divs[el])

    print(soup.prettify(formatter=None))

