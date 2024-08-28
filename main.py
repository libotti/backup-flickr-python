import os
import requests
from bs4 import BeautifulSoup
from alive_progress import alive_bar

# Importante: Instalar as bibliotecas necessárias
# pip install requests
# pip install beautifulsoup4
# pip install alive-progress

# Set the flicker_account_name, and destination folder
flicker_account_name = "mboficial"
dest = "D:/flickr-mboficial"

source = "https://www.flickr.com/"

def get_album_pages(account):
    uri_albums = f"https://www.flickr.com/photos/{account}/albums"
    print(uri_albums)

    # get the page
    page = requests.get(uri_albums)
    soup = BeautifulSoup(page.content, 'lxml')

    # get all hrefs inside div "view pagination-view" class
    album_divs = soup.find_all("div", class_="pagination-view")
    paginas = album_divs[0].find_all("a")

    # extract all href to one array
    href_list = []
    for pagina in paginas:
        linkPagina = f"{source}{pagina['href']}"
        if linkPagina.endswith("/"):
            linkPagina = linkPagina[:-1]

        if linkPagina not in href_list:
            href_list.append(f"{source}{pagina['href']}")

    return href_list


def get_album_urls(uri_album):
    num_page = uri_album.split("/")[7]

    # get the page
    page = requests.get(uri_album)
    soup = BeautifulSoup(page.content, 'lxml')

    # get all hrefs inside div "view pagination-view" class
    album_divs = soup.find_all("div", class_="view photo-list-view requiredToShowOnServer")
    albums = soup.find_all("a", class_="interaction-view")
    print(f"qtd albums na {num_page}: {len(albums)}")

    for album in albums:
        position = f"{albums.index(album) + 1} de {len(albums)}"
        get_album_photos(album['href'], album['title'], num_page, position)

def get_album_photos(uri_album, album_name, num_page, position):
    # create a dir for the album
    codigo_album = uri_album.split("/")[4]
    album_name = (album_name
                 .replace("  ", " ")
                 .replace(":", "_")
                 .replace("/", "_")
                 .replace("\\", "_")
                 .replace("?", "_")
                 .replace("!", "_")
                 .replace("&", "_")
                 .replace("=", "_")
                 .replace('"', "")
                 .replace("#", "_")
                 .replace("@", "_")
                 .replace("$", "_")
                 .replace("%", "_")
                 .replace("^", "_")
                 .replace("*", "_")
                 .replace("~", "_")
                 .replace("`", "_")
                 .replace("<", "_")
                 .replace(">", "_"))
    dir_album = f"{dest}/{codigo_album} - {album_name}/"

    if not os.path.exists(dir_album):
        os.makedirs(dir_album)

    # get the page
    page = requests.get(f"{source}{uri_album}")
    soup = BeautifulSoup(page.content, 'lxml')

    # get all hrefs inside div "view pagination-view" class
    photo_list_divs = soup.find_all("div", class_="photo-list-view")
    photos = photo_list_divs[0].find_all("a", class_="photo-link")
    #print(f"{uri_album} -> {dir_album} :: {len(photos)} photos")
    print(f"{num_page} | album {position} ({len(photos)} fotos) | {codigo_album} | {album_name}")

    with alive_bar(len(photos), force_tty=True, length=20, max_cols=120) as bar:
        for photo in photos:
            photo_link_url = photo['href'].split("/")
            phpage = f"{source}{photo_link_url[1]}/{photo_link_url[2]}/{photo_link_url[3]}/sizes/o/"
            # alcancar a pagina da foto na resolucao original e pegar o link da imagem
            # https://www.flickr.com/photos/mboficial/53924388837/sizes/o/

            # get the page
            page_photo = requests.get(phpage)
            soup_photo = BeautifulSoup(page_photo.content, 'lxml')

            div_download_all = soup_photo.find_all("div", {"id": "all-sizes-header"})
            downloads = div_download_all[0].find_all("a")
            photo_file = None
            photo_name = None

            try:
                # get all a with the text "Download the Original size of this photo"
                photo_file = requests.get(downloads[3]['href'])
                photo_name = photo_file.url.split("/")[4]

                bar.text = f"{photo_name}"
                if not os.path.exists(f"{dir_album}{photo_name}"):
                    with open(f"{dir_album}{photo_name}", 'wb') as f:
                        f.write(photo_file.content)

            except:
                print(f"Erro ao salvar {photo_name}: {photo}")
                print(f"   photo_link_url => {photo_link_url}")

            bar()

if __name__ == '__main__':
    lista_paginas = get_album_pages(flicker_account_name)

    for pagina in lista_paginas:
        get_album_urls(pagina)
