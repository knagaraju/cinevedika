"""
    Cinevedika Kodi Addon
    Copyright (C) 2016 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re, requests
import urlresolver
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_addonname = _addon.getAddonInfo('name')
_icon = _addon.getAddonInfo('icon')


#base_url = 'http://www.cinevedika.net/category/shows/etv-shows/jabardasth/'
base_url = 'http://www.cinevedika.net/category/'
shows = 'shows'
serials = 'telugu-serials'
MAINLIST = {shows: base_url+'shows/',
           serials: base_url + 'telugu-serials/'}

def get_categories():
    """
    Get the list of countries.
    :return: list
    """
    return MAINLIST.keys()

    
def get_channels(category):
    """
    Get the list of channels.
    :return: list
    """
    channels = []
    if category.lower() == shows.lower():
        channels.append(('etv-shows','etv-shows',base_url+category+'/etv-shows/'))
        channels.append(('maa-tv-shows','maa-tv-shows',base_url+category+'/maa-tv-shows/'))
        channels.append(('gemini-tv-shows','gemini-tv-shows',base_url+category+'/gemini-tv-shows/'))
        channels.append(('zee-telugu-tv-shows','zee-telugu-tv-shows',base_url+category+'/zee-telugu-tv-shows/'))
        channels.append(('rk-open-heart','rk-open-heart',base_url+'/abn'+'/rk-open-heart/'))
        channels.append(('encounter','encounter',base_url+'/tv9'+'/encounter/'))
    
    return channels


def get_shows(channel,category):
    """
    Get the list of shows.
    :return: list
    """
    shows = []
    items = []
    #import web_pdb; web_pdb.set_trace()
    html = requests.get(MAINLIST[category]).text
    mlink = SoupStrainer('div', {'class':'dropdown_4columns'})
    soup = BeautifulSoup(html, parseOnlyThese=mlink)
    if channel.endswith('etv-shows/') :
        items = soup.findAll("ul")[0].findAll("li")
    elif channel.endswith('maa-tv-shows/') : 
        items = soup.findAll("ul")[1].findAll("li")
        markup = '<li><a href="http://www.cinevedika.net/category/shows/maa-tv-shows/desamudurlu/" target="_blank" title="Desamudurlu Show Online">Desamudurlu</a></li>'
        soupdesam = BeautifulSoup(markup)
        items.insert(1, soupdesam.li)
    elif channel.endswith('gemini-tv-shows/') : 
        items = soup.findAll("ul")[2].findAll("li")
    elif channel.endswith('zee-telugu-tv-shows/') :
        items = soup.findAll("ul")[0].findAll("li")
    elif channel.endswith('rk-open-heart/') :
        items = soup.findAll("ul")[0].findAll("li")
    elif channel.endswith('encounter/') :
        items = soup.findAll("ul")[0].findAll("li")
                           
    for item in items:
        title = item.text
        url = item.a.get('href')
        icon = title
        
        shows.append((title,icon,url))
    
    return shows
    

def get_episodes(show):
    """
    Get the list of episodes.
    :return: list
    """
    #import web_pdb; web_pdb.set_trace()
    episodes = []
    html = requests.get(show).text
    mlink = SoupStrainer('div', {'id':'main'})
    soup = BeautifulSoup(html, parseOnlyThese=mlink)
    items = soup.findAll('div', {'class':'home_post_box'})
    for item in items:
        title = item.h3.a.text
        if 'written' not in title.lower():
            url = item.a.get('href')
            if url.startswith('/'):
                url = base_url[:-1] + url
            else:
                url = url
            try:
                icon = item.find('img')['src']
                if icon.startswith('/'):
                    icon = base_url[:-1] + icon
                else:
                    icon = icon
            except:
                icon = base_icon           
            episodes.append((title,icon,url))
    plink = SoupStrainer('a', {'class':'pagination-next'})
    soup = BeautifulSoup(html, parseOnlyThese=plink)
    if 'Next' in str(soup):
        icon = _icon
        ep_link = soup.a.get('href')
        if 'category' in ep_link:
            url = base_url[:-1] + ep_link
        else:
            url = show + ep_link
        title = 'Next Page: ' + url.split('page/')[1][:-1]
        episodes.append((title, icon, url))    
    return episodes


def get_videos(episode):
    """
    Get the list of videos.
    :return: list
    """
    #import web_pdb; web_pdb.set_trace()
    videos = []
    html = requests.get(episode).text
    mlink = SoupStrainer('div', {'class':'entry-content'})
    soup = BeautifulSoup(html, parseOnlyThese=mlink)
    items = soup.findAll('a', href=True)
    for item in items:
        try:
            vid_name = item['title']
        except:
            vid_name = item.text
        vid_url = item['href']
        videos.append((vid_name, vid_url))

    mlink = SoupStrainer('div', {'class':'post-content'})
    soup = BeautifulSoup(html, parseOnlyThese=mlink)
    #items = soup.findAll('div', {'class':'video-shortcode'})
    items = soup.findAll('iframe')
    for item in items:
        try:
            vid_name = item['title']
        except:
            vid_name = item['class']
        vid_url = item['src']
        videos.append((vid_name, vid_url))   
        
    return videos

def list_categories():
    """
    Create the list of categories in the Kodi interface.
    """
    categories = get_categories()
    listing = []
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        list_item.setInfo('video', {'title': category, 'genre': category})
        list_item.setArt({'thumb': _icon,
                          'icon': _icon,
                          'fanart': _icon})
        url = '{0}?action=list_category&category={1}'.format(_url, category)
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def list_channels(category):
    """
    Create the list of countries in the Kodi interface.
    """
    channels = get_channels(category)
    listing = []
    for channel in channels:
        list_item = xbmcgui.ListItem(label=channel[0])
        list_item.setArt({'thumb': channel[1],
                          'icon': channel[1],
                          'fanart': channel[1]})
        list_item.setInfo('video', {'title': channel[0], 'genre': category})
        url = '{0}?action=list_channel&channel={1}&category={2}'.format(_url, channel[2], category)
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)
    

def list_shows(channel,category):
    """
    Create the list of channels in the Kodi interface.
    """
    #import web_pdb; web_pdb.set_trace()
    shows = get_shows(channel,category)
    listing = []
    for show in shows:
        list_item = xbmcgui.ListItem(label=show[0])
        list_item.setArt({'thumb': show[1],
                          'icon': show[1],
                          'fanart': show[1]})
        list_item.setInfo('video', {'title': show[0], 'genre': 'www.CineVedika.net'})
        url = '{0}?action=list_show&show={1}'.format(_url, show[2])
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

    
def list_episodes(show):
    """
    Create the list of episodes in the Kodi interface.
    """
    #import web_pdb; web_pdb.set_trace()
    episodes = get_episodes(show)
    listing = []
    for episode in episodes:
        list_item = xbmcgui.ListItem(label=episode[0])
        list_item.setArt({'thumb': episode[1],
                          'icon': episode[1],
                          'fanart': episode[1]})
        list_item.setInfo('video', {'title': episode[0], 'genre': 'http://www.cinevedika.net'})
        if 'Next Page' not in episode[0]:
            url = '{0}?action=list_episode&episode={1}&icon={2}'.format(_url, episode[2], episode[1])
        else:
            url = '{0}?action=list_show&show={1}'.format(_url, episode[2])
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)
    
    
def list_videos(episode,icon):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: str
    """

    videos = get_videos(episode)
    listing = []
    for video in videos:
        list_item = xbmcgui.ListItem(label=video[0])
        list_item.setArt({'thumb': icon,
                          'icon': icon,
                          'fanart': icon})
        list_item.setInfo('video', {'title': video[0], 'genre': 'http://www.cinevedika.net'})
        list_item.setProperty('IsPlayable', 'true')
        url = '{0}?action=play&video={1}'.format(_url, video[1])
        is_folder = False
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def resolve_url(url):
    duration=5000   
    try:
        stream_url = urlresolver.HostedMediaFile(url=url).resolve()
        # If urlresolver returns false then the video url was not resolved.
        if not stream_url or not isinstance(stream_url, basestring):
            try: msg = stream_url.msg
            except: msg = url
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('URL Resolver',msg, duration, _icon))
            return False
    except Exception as e:
        try: msg = str(e)
        except: msg = url
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('URL Resolver',msg, duration, _icon))
        return False
        
    return stream_url


def play_video(path):
    """
    Play a video by the provided path.

    :param path: str
    """
    import web_pdb; web_pdb.set_trace()
    # Create a playable item with a path to play.
    videos = []
    html = requests.get(path).text
    mlink = SoupStrainer('div', {'class':re.compile(r'video\p')})
    soup = BeautifulSoup(html, parseOnlyThese=mlink)
    stream_url=re.findall(r'(http[s]?://\S+)', soup.text)[1]
    print stream_url
    #url=resolve_url(stream_url)
    #print url
    play_item = xbmcgui.ListItem(path=path)
    play_item.setPath(re.sub(r'^"|"$', '', stream_url))
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    #import web_pdb; web_pdb.set_trace()
    if params:
        if params['action'] == 'list_category':
            list_channels(params['category'])
        elif params['action'] == 'list_channel':
            list_shows(params['channel'],params['category'])
        elif params['action'] == 'list_show':
            list_episodes(params['show'])
        elif params['action'] == 'list_episode':
            list_videos(params['episode'],params['icon'])
        elif params['action'] == 'play':
            play_video(params['video'])
    else:
        list_categories()
        #list_channels('Indian')


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
