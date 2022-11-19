import time

import pytest

from ultimakerpy.client import FutureResult, UMClient, _BatchClient, _RealtimeClient

NUM_REQUESTS = 5
URL_GET = 'http://httpbin.org/get'
URL_PUT = 'http://httpbin.org/put'
URL_POST = 'http://httpbin.org/post'
URL_INVALID = 'invalid'


def test_realtime_client():
    print('_RealtimeClient')
    client = _RealtimeClient()
    t1 = time.time()
    for i in range(NUM_REQUESTS):
        print('request', i)
        client.get(URL_GET)
        client.put(URL_PUT, {'target': i})
        client.post(URL_POST, {'target': i})
    t2 = time.time()
    print('time:', t2-t1, 'sec')


def test_batch_client():
    print('_BatchClient')
    client = _BatchClient()
    t1 = time.time()
    for i in range(NUM_REQUESTS):
        client.register_get(URL_GET)
        client.register_put(URL_PUT, {'target': i})
        client.register_post(URL_POST, {'target': i})
    print('batch request')
    client.batch_request()
    t2 = time.time()
    print('time:', t2-t1, 'sec')


def test_um_client():
    print('UMClient')
    client = UMClient()
    t1 = time.time()
    for i in range(NUM_REQUESTS):
        print('request', i)
        client.get(URL_GET)
        client.put(URL_PUT, {'target': i})
        client.post(URL_POST, {'target': i})
    t2 = time.time()
    with client.batch_mode():
        for i in range(NUM_REQUESTS):
            client.get(URL_GET)
            client.put(URL_PUT)
            client.post(URL_POST)
        print('batch request')
    t3 = time.time()
    print('time-realtime:', t2-t1, 'sec')
    print('time-batch   :', t3-t2, 'sec')

    with pytest.raises(Exception):
        client.get(URL_INVALID)


def test_future_result():
    future = FutureResult()
    with pytest.raises(Exception):
        future.get()
    future.store(0)
    with pytest.raises(Exception):
        future.store(1)
    assert future.get() == 0


if __name__ == '__main__':
    test_realtime_client()
    test_batch_client()
    test_um_client()
    test_future_result()
