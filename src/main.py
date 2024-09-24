import feedparser
import requests
import json
import re

# variables need to login to qbittorrent
qbittorrent_login_username = ""
qbittorrent_login_password = ""
qbittorrent_url = ""

# array of torrents to add to qbittorrent
torrents = []

# array make from the distro_regex.json file
regex_distro = []
# rss url to the distrowatch torrent list
rss_url = "https://distrowatch.com/news/torrents.xml"
# titles from the distrowatch rss feed
rss_title = []
# links from the distrowatch rss feed
rss_link = []

# parse the distrowatch rss feed
feed = feedparser.parse(rss_url)
# if status code is 200 loop to the entries and adds the title and links to the arrays
if feed.status == 200:
    for entry in feed.entries:
        # print(entry.title)
        rss_title.append(entry.title)
        # print(entry.link)
        rss_link.append(entry.link)
    else:
        # print the status code if it is not 200
        print("failed to get rss feed. status code:", feed.status)

# open distro_regex.json and load as json
with open("src/distro_regex.json") as distro_regex:
    distro_regex_josn = json.load(distro_regex)
    # loop to distro_regex_josn and add the regex to the regex_distro array
    for entry in distro_regex_josn:
        regex_distro.append(entry["regex"])

# loop to regex_distro
for regex_distro_index, regex_distro in enumerate(regex_distro):
    # loop to rss_title and if title match the regex add rss_link to torrents array
    for title_index, title in enumerate(rss_title):
        regex = re.compile(regex_distro)
        if regex.fullmatch(title):
            print(title)
            print(rss_link[title_index])
            torrents.append(rss_link[title_index])


# -------------------------------- qbittorrent_login -----------------------------------------------------------------------------------------------

# open config.json and load it as json and set the login variables
with open("src/config.json") as config:
    config_josn = json.load(config)
    print("config_josn: "+str(config_josn))
    qbittorrent_login_username = config_josn[0]["username"]
    print("qbittorrent_login_username: " + qbittorrent_login_username)
    qbittorrent_login_password = config_josn[0]["password"]
    print("qbittorrent_login_password: "+qbittorrent_login_password)
    qbittorrent_url = config_josn[0]["qbittorrent"]
    print("qbittorrent_url: "+qbittorrent_url)

# url to login to the qbittorrent api
url = qbittorrent_url+"/api/v2/auth/login"
print("qbittorrent_login_url: "+url)
# data for the login request
qbittorrent_login_payload = "username="+qbittorrent_login_username + \
    "&"+"password="+qbittorrent_login_password
print("qbittorrent_login_payload: "+qbittorrent_login_payload)
# headers for the login request
qbittorrent_login_headers = {
    'Referer': qbittorrent_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}
print("qbittorrent_login_headers: "+str(qbittorrent_login_headers))
# sends the login request
qbittorrent_login_response = requests.request(
    "POST", url, headers=qbittorrent_login_headers, data=qbittorrent_login_payload)
print("qbittorrent_login_response.status_code: " +
      str(qbittorrent_login_response.status_code))
print("qbittorrent_login_response.headers[set-cookie].split(;)[0]: " +
      qbittorrent_login_response.headers["set-cookie"].split(";")[0])
print("qbittorrent_login_response.text: " + qbittorrent_login_response.text)

# -------------------------------- qbittorrent_add ----------------------------------------------------------------------------------------------

# url for the qbittorrent api to add torrent
url = qbittorrent_url+"/api/v2/torrents/add"

# loop torrents array
for torrents_index, torrents in enumerate(torrents):
    # data for the add torrent request
    payload = {
        'root_folder': 'true',
        'urls': torrents
    }
    # headers for the add torrent request
    headers = {
        "referer": qbittorrent_url+"/upload.html",
        "Origin": qbittorrent_url,
        "host": qbittorrent_url,
        "Cookie": qbittorrent_login_response.headers["set-cookie"].split(";")[0]
    }
    # sends the add torrent request
    response = requests.request("POST", url, headers=headers, data=payload)
    print("response.text: "+response.text)
