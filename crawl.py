import requests
import click
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

def download_pdfs(agenda_link, output_dir):
    r = requests.get(agenda_link)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href', '')
        if href != '':
            if 'sp_note' not in href and 'minutes' not in href and '#' not in href:
                pdf_link = urljoin(agenda_link, href)
                pdf_file = pdf_link.split('/')[-1]
                with open(os.path.join(output_dir, pdf_file), 'wb') as f:
                    print("Downloading", pdf_file)
                    pdf_r = requests.get(pdf_link)
                    f.write(pdf_r.content)


@click.command()
@click.option('--year', help='year', type=int, required=True)
@click.option('--output-dir', help='output directory', required=True)
def crawl(year, output_dir):
    if year >= 2000:
        year -= 2000
    url = 'https://www.legco.gov.hk/yr%d-%d/chinese/fc/fc/general/meetings.htm' % (year - 1, year)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) == 0:
            continue
        links = cells[0].find_all('a')
        for link in links:
            if '#s' == link.get('href', ''):
                second_cell = cells[1]
                agenda_link = second_cell.find('a')
                if agenda_link is not None:
                    download_pdfs(urljoin(url, agenda_link['href']), output_dir)
                    return

if __name__ == '__main__':
    crawl()
