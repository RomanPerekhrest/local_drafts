import asyncio
import aiohttp
from aiohttp import web, http_exceptions
import tqdm
import time
import collections
import os

Result = collections.namedtuple('Result', 'status data')

HTTPStatus = Enum('Status', 'ok not_found error')

DEST_DIR = './datafiles'
BASE_URL = 'https://dataverse.harvard.edu/api/access/datafile/'
DATAFILE_MAP = { '1374925': '2004', '1374923': '2005',
                 '1374922': '2006', '1374918': '2007', '1374917': '2008' }

MAX_CONQUR_REQ = 10

class FetchError(Exception):
    def __init__(self, data_idx):
        self.data_index = data_idx


@asyncio.coroutine
def get_datafile(data_idx, base_url):
    url = base_url + data_idx
    
    with aiohttp.ClientSession() as sesion:
        # resp = yield from aiohttp.request('GET', url)
        resp = yield from sesion.request('GET', url)
        if resp.status == 200:
            datafile = yield from resp.read()
            return datafile
        elif resp.status == 404:
            raise web.HTTPNotFound()
        else:
            raise http_exceptions.HttpProcessingError(
                code=resp.status,
                message=resp.reason, headers=resp.headers)


@asyncio.coroutine
def save_datafile(datafile, data_idx):
    filename = DATAFILE_MAP[data_idx] + '.csv.bz2'
    path = os.path.join(DEST_DIR, filename)
    
    with open(path, 'wb') as f:
        print('saving to ', path)
        f.write(datafile)


@asyncio.coroutine
def download_datafile(data_idx, base_url, semaphore, verbose):
    try:
        with (yield from semaphore):
            datafile = yield from get_datafile(data_idx, base_url)
    except web.HTTPNotFound:
        status = HTTPStatus.not_found
        msg = 'not found'
    except Exception as exc:
        raise FetchError(data_idx) from exc
    else:
        save_datafile(datafile, data_idx)
        status = HTTPStatus.ok
        msg = 'not found'

    if verbose and msg:
        print(DATAFILE_MAP[data_idx], msg)

    return Result(status, data_idx)


@asyncio.coroutine
def supervise_coroutines(data_indices, base_url, concur_req, verbose):
    counter = collections.Counter()
    semaphore = asyncio.Semaphore(concur_req)

    to_do_coroutines = asyncio.as_completed(
        [download_datafile(d_idx, base_url, semaphore, verbose)
          for d_idx in data_indices])

    if not verbose:
        to_do_coroutines = tqdm.tqdm(to_do_coroutines, total=len(data_indices))
    for future in to_do_coroutines:
        try:
            res = yield from future
        except FetchError as exc:
            data_idx = exc.data_index
            try:
                error_msg = exc.__cause__.args[0]
            except IndexError:
                error_msg = exc.__cause__.__class__.__name__
            if verbose and error_msg:
                print('*** Error for time period {}: {}'.format(DATAFILE_MAP[data_idx], error_msg))
            status = HTTPStatus.error
        else:
            status = res.status
            print('--- {}.csv.bz2 downloaded'.format(DATAFILE_MAP[res.data]))

        counter[status] += 1

    return counter


def batch_download(data_indices, base_url, concur_req, verbose):
    loop = asyncio.get_event_loop()
    supervisor = supervise_coroutines(data_indices, base_url, concur_req, verbose)
    result = loop.run_until_complete(supervisor)
    loop.close()
    return result


def main(batch_downloader, verbose=False):
    t0 = time.time()
    counts = batch_downloader(DATAFILE_MAP.keys(), BASE_URL, MAX_CONQUR_REQ, verbose)
    elapsed = time.time() - t0
    print('Datafiles downloaded in {:.2f}s'.format(elapsed))
    print('Stat info: ', counts)


if __name__ == '__main__':
    main(batch_downloader=batch_download)

