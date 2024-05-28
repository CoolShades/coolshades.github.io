import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from scholarly import scholarly

# Retrieve the author's metrics
user_id = '4SM2zgsAAAAJ'
author = scholarly.search_author_id(user_id)
full_author = scholarly.fill(author)
h_index = full_author['hindex']
i10_index = full_author['i10index']
citations = full_author['citedby']

# URL to your PubMed RSS feed
RSS_FEED_URL = 'https://pubmed.ncbi.nlm.nih.gov/rss/search/1h5ksaKdwjS0xlIYu5mS9DduNaClI9Wd466NAE2IrWIhXsVgNo/?limit=50&utm_campaign=pubmed-2&fc=20240528054916'

response = requests.get(RSS_FEED_URL)
root = ET.fromstring(response.content)

# Namespace for parsing the RSS feed
ns = {'dc': 'http://purl.org/dc/elements/1.1/', 'content': 'http://purl.org/rss/1.0/modules/content/'}

# Variants of your name to be bolded and italicized
name_variants = ["Uthayachandran Bhalraam", "U Bhalraam", "Bhalraam U"]

publications = []

for item in root.findall('./channel/item'):
    title = item.find('title').text
    link = item.find('link').text
    pub_date = item.find('pubDate').text
    creators = [creator.text for creator in item.findall('dc:creator', ns)]
    source = item.find('dc:source', ns).text if item.find('dc:source', ns) is not None else 'No Source'

    # Parse the publication date to extract the year
    pub_year = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').year
    
    publication = {
        'title': title,
        'link': link,
        'creators': creators,
        'source': source,
        'year': pub_year
    }
    publications.append(publication)

def bold_and_italicize_name(text, name_variants):
    for name in name_variants:
        text = text.replace(name, f"<u>{name}</u>")
    return text

def capitalize_each_word(text):
    return ' '.join([word.capitalize() for word in text.split()])

# Generate markdown
with open('publications.md', 'w') as file:
    pub_count = len(publications)
    file.write('---\n')
    file.write('layout: single\n')
    file.write(f'title: "Publications ({pub_count})"\n')
    file.write('permalink: /publications/\n')
    file.write('author_profile: true\n')
    file.write('---\n\n')

    file.write('<style>hr { display: none; }</style>\n\n')

    file.write(f"<p style='font-size: 0.7em;'><i>Citations: <u>{citations}</u>; h-index: <u>{h_index}</u>; i10-index: <u>{i10_index}</u></i></p>\n")

    for pub in publications:
        creators_str = ', '.join([bold_and_italicize_name(creator, name_variants) for creator in pub['creators']])
        source_str = capitalize_each_word(pub['source'])

        file.write(f"#### [{pub['title']}]({pub['link']})<br>")
        file.write(f"<span style='font-size: 0.55em;'>{creators_str}</span><br>")  # Adjust font size for authors
        file.write(f"<span style='font-size: 0.85em;'><i>{source_str}, {pub['year']}</i></span>\n")  # Journal name and year

    file.write("<p style='font-size: 0.7em;'><br><br><i>This page was entirely programmatically generated using a <a href='https://github.com/CoolShades/coolshades.github.io/blob/master/_python/publications.py'>Python script</a>. The script retrieves publication data from PubMed using an RSS feed, processes it to extract relevant information such as title, authors, journal, and publication year, and formats it into markdown. Additionally, it retrieves the author's citation metrics from Google Scholar. The page content is dynamically created based on this data.</i></p>")
    file.write(f"<p style='font-size: 0.7em;'><i>This page was last updated @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i></p>\n\n")

print("Publications have been saved to publications.md")
