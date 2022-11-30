import asyncio
import atexit
import json
from typing import Any, Dict, Optional
import warnings
from contextlib import contextmanager

import aiohttp
import requests
from requests.auth import HTTPDigestAuth

from .exceptions import FutureResultError, RequestError, RequestModeWarning


class UMClient:

    def __init__(
            self, timeout: Optional[float] = None,
            username: Optional[str] = None,
            password: Optional[str] = None) -> None:
        auth = None
        if username is not None and password is not None:
            auth = HTTPDigestAuth(username, password)
        self._rclient = _RealtimeClient(auth=auth, timeout=timeout)
        self._bclient = _BatchClient(timeout=timeout)
        self.__is_batch_mode = False
        self.__future_results = []

    @contextmanager
    def batch_mode(self) -> None:
        try:
            self.__is_batch_mode = True
            yield
        finally:
            for fut, res in zip(self.__future_results,
                                self._bclient.batch_request()):
                fut.store(res)
            self.__is_batch_mode = False
            self.__future_results = []

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        if not self.__is_batch_mode:
            return self._rclient.get(url, headers=headers)
        else:
            self._bclient.register_get(url, headers=headers)
            return self.__generate_future_result()

    def put(
            self, url: str, data: Optional[Any] = None,
            files: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None) -> None:
        if self.__is_batch_mode:
            warnings.warn('batch mode does not currently support put method',
                          RequestModeWarning, stacklevel=2)
        if data is not None: data = json.dumps(data)
        if files is not None: files = json.dumps(files)
        return self._rclient.put(url, data=data, files=files, headers=headers)

    def post(
            self, url: str, data: Optional[Any] = None,
            files: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None) -> None:
        if self.__is_batch_mode:
            warnings.warn('batch mode does not currently support post method',
                          RequestModeWarning, stacklevel=2)
        if data is not None: data = json.dumps(data)
        return self._rclient.post(url, data=data, files=files, headers=headers)

    def __generate_future_result(self) -> 'FutureResult':
        future_result = FutureResult()
        self.__future_results.append(future_result)
        return future_result


class _RealtimeClient:

    def __init__(self, auth=None, timeout=None):
        self.auth = auth
        self.timeout = timeout

    def get(self, url, headers=None):
        resp = requests.get(url=url, headers=headers, auth=self.auth,
                            timeout=self.timeout)
        return self._parse_response(resp)

    def put(self, url, data=None, files=None, headers=None):
        resp = requests.put(url=url, data=data, files=files,
                            headers=headers, auth=self.auth,
                            timeout=self.timeout)
        return self._parse_response(resp)

    def post(self, url, data=None, files=None, headers=None):
        resp = requests.post(url=url, data=data, files=files,
                             headers=headers, auth=self.auth,
                             timeout=self.timeout)
        return self._parse_response(resp)

    def _parse_response(self, resp):
        code = resp.status_code
        try:
            respj = resp.json()
        except requests.JSONDecodeError:
            respj = ''
        if code > 400:
            raise RequestError('status code {}: {}'.format(code, respj))
        return respj


class _BatchClient:

    def __init__(self, auth=None, timeout=None):
        self.auth = auth
        self._tasks = []
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._session = aiohttp.ClientSession(
            auth=auth, loop=self._loop,
            timeout=aiohttp.ClientTimeout(timeout))
        atexit.register(
            lambda: self._loop.run_until_complete(self._session.close()))

    def register_get(self, url, headers=None):
        self.__register(self.__get(url, headers=headers))

    def register_put(self, url, data=None, headers=None):
        self.__register(self.__put(url, data=data, headers=headers))

    def register_post(self, url, data=None, headers=None):
        self.__register(self.__post(url, data=data, headers=headers))

    def batch_request(self):
        results = self._loop.run_until_complete(asyncio.gather(*self._tasks))
        self._tasks = []
        return results

    def __register(self, coro):
        self._tasks.append(self._loop.create_task(coro))

    async def __get(self, *args, **kwargs):
        resp = await self._session.get(*args, **kwargs)
        return await self._parse_response(resp)

    async def __put(self, *args, **kwargs):
        resp = await self._session.put(*args, **kwargs)
        return await self._parse_response(resp)

    async def __post(self, *args, **kwargs):
        resp = await self._session.post(*args, **kwargs)
        return await self._parse_response(resp)

    async def _parse_response(self, resp):
        code = resp.status
        respj = await resp.json()
        if code > 400:
            raise RequestError('status code {}: {}'.format(code, respj))
        return respj


class FutureResult:

    def __init__(self):
        self.__value = None
        self.__slice_items = []

    def __getitem__(self, item):
        self.__slice_items.append(item)
        return self

    def store(self, value: Any) -> None:
        if self.__value is not None:
            raise FutureResultError('value already stored')
        self.__value = value

    def get(self) -> None:
        if self.__value is None:
            raise FutureResultError('value not stored')
        if len(self.__slice_items) > 0:
            return self.__value[self.__slice_items.pop(0)]
        return self.__value
