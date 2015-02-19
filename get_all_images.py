def img_page_info(url):
    '''Retrieves image information from the image page'''
    # Set the page to show only adults
    req = Request(url, headers={'Cookie': 'stage_filter=adults'})
    response = urlopen(req)
    soup = bs(urlopen(req))

    img_urls = []
    nametags = []
    leveltags = []
    moveToNext = True

    # For each box, save the relevant information
    boxes = soup.findAll('td', attrs={'class':['node-main', 'node-main-alt']})
    if len(boxes) == 0:
        return img_urls, nametags, leveltags
    for b in boxes:
        img_url = []
        level = ''
        name = ''
        bc = b.findChildren()
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
        img_urls.append(img_url)
        nametags.append(name)
        leveltags.append(level)
    if (len(boxes) == 1):
        moveToNext = True
    else:
        moveToNext = False
    return moveToNext, img_urls, nametags, leveltags