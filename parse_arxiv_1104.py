import json, re, sys, os
import xml.etree.ElementTree as ET

NS = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}


def parse(path):
    out = []
    tree = ET.parse(path)
    root = tree.getroot()
    for e in root.findall('a:entry', NS):
        def t(tag):
            el = e.find(tag, NS)
            return (el.text or '').strip() if el is not None else ''
        aid = t('a:id')
        m = re.search(r'abs/([^v]+)v?(\d*)', aid)
        pid = m.group(1) if m else aid
        cats = [c.get('term') for c in e.findall('a:category', NS)]
        authors = [a.find('a:name', NS).text for a in e.findall('a:author', NS) if a.find('a:name', NS) is not None]
        out.append({
            'id': pid,
            'title': re.sub(r'\s+', ' ', t('a:title')),
            'summary': re.sub(r'\s+', ' ', t('a:summary')),
            'published': t('a:published'),
            'updated': t('a:updated'),
            'authors': authors,
            'cats': cats,
            'abs_url': 'https://arxiv.org/abs/' + pid,
        })
    return out


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    data = parse(src)
    json.dump(data, open(dst, 'w'), ensure_ascii=False, indent=1)
    print(dst, len(data))
