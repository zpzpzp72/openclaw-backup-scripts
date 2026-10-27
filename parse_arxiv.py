import json, sys, re
import xml.etree.ElementTree as ET

NS = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

def parse(path, out):
    tree = ET.parse(path)
    root = tree.getroot()
    items = []
    for e in root.findall('a:entry', NS):
        eid = e.find('a:id', NS).text.split('/abs/')[-1]
        title = ' '.join(e.find('a:title', NS).text.split())
        summ = ' '.join(e.find('a:summary', NS).text.split())
        pub = e.find('a:published', NS).text
        upd = e.find('a:updated', NS).text
        cats = [c.get('term') for c in e.findall('a:category', NS)]
        authors = [a.find('a:name', NS).text for a in e.findall('a:author', NS)]
        link = ''
        for l in e.findall('a:link', NS):
            if l.get('rel') == 'alternate':
                link = l.get('href')
        items.append({'id': eid, 'title': title, 'summary': summ, 'published': pub,
                      'updated': upd, 'cats': cats, 'authors': authors, 'link': link})
    json.dump(items, open(out, 'w'), ensure_ascii=False, indent=1)
    print(out, len(items), 'entries; date range:', items[0]['published'][:10], '->', items[-1]['published'][:10])

if __name__ == '__main__':
    parse(sys.argv[1], sys.argv[2])
