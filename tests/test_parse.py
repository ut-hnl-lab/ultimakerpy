import json
from pprint import pprint
import yaml
from ultimakerpy import UMS3
from ultimakerpy.const import CONFIG, ENDPOINT
from ultimakerpy.parse import parse_endpoints

NAME = 'main'
MTYPE = 's3'


def test_parse():
    with open(CONFIG, 'r') as f:
        config: dict = yaml.safe_load(f)[NAME]

    with open(ENDPOINT, 'r') as f:
        item = json.load(f)[MTYPE]

    url, lim = parse_endpoints(
        item=item,
        base_path='http://{ip_address}'.format(
            ip_address=config['ip_address']))

    pprint(url)
    pprint(lim)


if __name__ == '__main__':
    test_parse()
