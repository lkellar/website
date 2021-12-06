from datetime import datetime
from os import path
import re
import json
from dominate import tags, document
from dominate.util import raw

current_dir = path.dirname(path.realpath(__file__))

urls = re.compile(r'\[([^\]]*)]\(([^\)]*)\)')

def generateHtml():
    with open(path.join(current_dir, '../changelog/', 'storage.json'), 'r') as f:
        data = json.load(f)[::-1]

    doc = document(title='Changelog - lkellar.org')

    articles = []

    with doc.head:
        tags.link(rel='stylesheet', href='style.css')
        tags.meta(charset="UTF-8")
        tags.meta(name="description", content="A log of all changes made on lkellar.org")
        tags.meta(name="viewport", content="width=device-width, initial-scale=1")
        tags.link(rel="alternate", title="Changelog Feed", type="application/json",
                  href="https://lkellar.org/changelog/feed.json")

    with doc:
        with tags.nav().add(tags.ol()):
            with tags.li():
                tags.a("Home", href="../")
            tags.li("Changelog")

        with tags.main():
            tags.h1('Changelog')
            for entry in data:
                tags.hr()
                article_content = tags.article()

                with article_content:
                    tags.h2(f'{entry["title"]} - {entry["date"].split("T")[0]}',
                            id=f'{entry["title"]} - {entry["date"]}'.replace(' ', ''.lower()))

                    list_content = tags.ul()
                    with list_content:
                        for line in entry['items']:
                            line = urls.sub(r'<a href="\2">\1</a>', line)
                            tags.li(raw(line))

                articles.append((f'{entry["title"]} - {entry["date"]}'.replace(' ', ''.lower()),
                                 list_content.render(), entry["date"], entry['title']))

    with open(path.join(current_dir, '../changelog/', 'index.html'), 'w') as f:
        f.write(doc.render())

    generateFeed(articles)

def generateFeed(articles: list):
    articles = [{
        "id": i[0],
        "content_html": i[1],
        "url": f'https://lkellar.org/changelog/#{i[0]}',
        "date_published": i[2],
        "title": i[3]
    } for i in articles]

    with open(path.join(current_dir, '../changelog/', 'feed.json'), 'r') as f:
        data = json.load(f)

    data['items'] = articles

    with open(path.join(current_dir, '../changelog/', 'feed.json'), 'w') as f:
        json.dump(data, f)


def appendToJson(title: str, content: list):
    with open(path.join(current_dir, '../changelog/', 'storage.json'), 'r') as f:
        data = json.load(f)

    new_entry = {
        "title": title,
        "date": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "items": content
    }

    data.append(new_entry)

    with open(path.join(current_dir, '../changelog/', 'storage.json'), 'w') as f:
        json.dump(data, f)
