from urllib.parse import urljoin


def parse_endpoints(items, base_path='', url={}, lim={}):
    for item in items:
        path = urljoin(base_path, item['path'])
        if 'endpoints' in item.keys():
            u, l = _parse_endpoints(item['endpoints'], path)
            url = _merge_subdict(url, u)
            lim = _merge_subdict(lim, l)
        if 'items' in item.keys():
            url, lim = parse_endpoints(item['items'], path, url, lim)
    return url, lim


def _parse_endpoints(endpoints, base_path):
    url = dict()
    lim = dict()
    cats = set()
    for ep in endpoints:
        cat = ep['category']
        if not cat in cats:
            url[cat] = {}
            lim[cat] = {}
            cats.add(cat)

        key = ep['label']
        if 'path' in ep.keys():
            url[cat].update({key: urljoin(base_path, ep['path'])})
        else:
            url[cat].update({key: base_path[:-1]})
        if 'inputlim' in ep.keys():
            lim[cat].update({key: ep['inputlim']})
    return (url, lim)


def _merge_subdict(d1, d2):
    for key, sd in(d2).items():
        if key not in d1.keys():
            d1[key] = sd
            continue
        d1[key].update(sd)
    return d1
