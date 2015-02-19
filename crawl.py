from BeautifulSoup import BeautifulSoup as bs
from urllib2 import urlopen, Request
from lxml import etree
import json, re

def createItem(url, currentNodeLevel, currentNodeName):
    '''Create individual items with name, level,  url, children attributes'''
    # Get all the urls in a single page in order
    response = urlopen(url)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    urls = tree.xpath('//span[@class="bgpage-taxon-desc"]//a/@href')[4:]
    soup = bs(urlopen(url))
    # Get all the names in a single page in order
    names = [x.text for x in soup.findAll('span', attrs={"class":"bgpage-taxon-desc"})][4:]
    # Get all the levels in a single page in order
    levels = [x.text for x in soup.findAll('span', attrs={"class":"bgpage-taxon-title"})][4:]

    index = names.index(currentNodeName)
    item = dict()
    item['Name'] = names[index]
    item['Level'] = levels[index]
    item['URL'] = urls[index]

    moveToNext, img_urls, nametag, leveltag = img_page_info(url[:-5] + '/bgimage')
    # If the first block's name matches the currentNode's name, save the image urls
    if compareNames(nametag, currentNodeName):
        currurl = url[:-5] + '/bgimage'
        while moveToNext:
            nexturl = nextPageURL(currurl)
            moveToNext, tmp_url, tmp_name, tmp_level = img_page_info(nexturl)
            img_urls += tmp_url
            currurl = nexturl
        item['Images'] = img_urls
    # Otherwise, leave the image field as blank.
    else:
        item['Images'] = []
    item['Children'] = []

    return item

def add_children(item, url, currentNodeLevel, currentNodeName):
    '''fill in the children attributes'''
    response = urlopen(url)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    urls = tree.xpath('//span[@class="bgpage-taxon-desc"]//a/@href')[4:]
    soup = bs(urlopen(url))
    # Get all the names in a single page in order
    names = [x.text for x in soup.findAll('span', attrs={"class":"bgpage-taxon-desc"})][4:]
    # Get all the levels in a single page in order
    levels = [x.text for x in soup.findAll('span', attrs={"class":"bgpage-taxon-title"})][4:]

    # Determine which index is the children of the current node
    children_start_index = 0
    for i in xrange(len(levels)):
        if levels[i] == currentNodeLevel:
            children_start_index = i+1
            break

    # Retrieve the list of children information recursively
    children_levels = levels[children_start_index:]
    children_names = names[children_start_index:]
    children_urls = urls[children_start_index:]
    if (len(children_names) == 0):
        item['Children'] = []
        return item
    for i in xrange(len(children_levels)):
        print "Accessing " + children_names[i] + "..."
        child = createItem(children_urls[i], children_levels[i], children_names[i])
        item['Children'].append(child)
        add_children(child, children_urls[i], children_levels[i], children_names[i])
        #print item
    return item

def img_page_info(url):
    '''Get image information from the given url'''
    req = Request(url, headers={'Cookie': 'stage_filter=adults'})
    response = urlopen(req)
    soup = bs(urlopen(req))

    moveToNext = False
    img_url = []
    level = ''
    name = ''

    boxes = soup.findAll('td', attrs={'class':['node-main', 'node-main-alt']})
    if len(boxes) == 1:
        moveToNext = True
    try:
        #Only consider the top box as it is the most relevant
        box = boxes[0]
        img_url = []

        bc = box.findChildren()
        name = bc[0].text.replace('&nbsp;', ' ')
        name = name.replace('&raquo;', ' / ')
        level = ' / '.join([x['title'] for x in bc[0].findChildren()])
        for i in xrange(len(bc)):
            try:
                if bc[i].img['class'] == 'bgimage-thumb':
                    imgsoup = bs(urlopen(bc[i]['href']))
                    img_url.append(imgsoup.findAll('img', attrs={'class':'bgimage-image'})[0]['src'])
                level += bc[i]['title']
                level += ' / '
            except KeyError:
                pass
            except TypeError:
                pass
    except IndexError:
        pass
    
    return moveToNext, img_url, name, level

def nextPageURL(prev):
    '''Get the url for the next page in image'''
    base_url = prev.split('=')[0]
    if len(prev.split('=')) == 1:
        return (base_url + '?from='+ str(24))
    else:
        num = prev.split('=')[1]
        return str(base_url + '=' + str((int)(num) + 24))

def compareNames(fromImg, fromTree):
    '''Compare the names from image page and tree page and Determine
       if the image should be included in the current node of the data'''
    tr = ' - '.join([x.strip() for x in fromTree.split('-')[1:]])
    #im = fromImg.split(' / ')[-1].split(' (')[0]
    return (tr in fromImg)

if __name__ == '__main__':
    start_url = "http://bugguide.net/node/view/81/tree"
    start_name = "Papilionoidea- Butterflies (excluding skippers)"
    start_level = "Superfamily"
    data = createItem(start_url, start_level, start_name)
    data = add_children(data, start_url, start_level, start_name)
    #test_url = "http://bugguide.net/node/view/28235/tree"
    #test_name = "zelicaon- Anise Swallowtail"
    #test_level = "Species"
    #testdata = createItem(test_url, test_level, test_name)
    #testdata = add_children(testdata, test_url, test_level, test_name)

    # Save the final data as json file
    print("Encoding the data in to json file...")
    with open('butterflies2.json', 'w') as outfile:
        json.dump(data, outfile)

