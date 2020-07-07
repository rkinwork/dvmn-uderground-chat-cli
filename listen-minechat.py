import asyncio
import contextlib
import sys
import datetime

import aiofiles
from aiofiles.os import wrap as aiowrap
import configargparse

SERVER_HOST = 'minechat.dvmn.org'
SERVER_PORT = 5000
ATTEMPT_DELAY_SECS = 3
ATTEMPTS_BEFORE_DELAY = 2
DEFAULT_HISTORY_FILE = 'minechat.history'
LOG_DTTM_TMPL = '%d-%m-%y %H:%M:%S'

DEFAULT_LOG_DESCRIPTOR = aiowrap(sys.stdout.write)


def decorate_log_file_descriptor(fd=None):
    if fd is None:
        write = DEFAULT_LOG_DESCRIPTOR
    else:
        if getattr(fd, 'write', None) is None:
            raise Exception("There is no write in file descriptor")
        write = fd.write

    async def wrapper(s):
        await write(f"[{datetime.datetime.now().strftime(LOG_DTTM_TMPL)}] {s}\n")

    return wrapper


@contextlib.asynccontextmanager
async def open_connection(server, port, rf_writer):
    attempt = 0
    connected = False
    reader, writer = None, None
    while True:
        try:
            reader, writer = await asyncio.open_connection(server, port)
            await rf_writer("Соединение установлено")
            connected = True
            yield reader, writer
            break

        except asyncio.CancelledError:
            raise

        except (ConnectionRefusedError, ConnectionResetError):
            if connected:
                await rf_writer("Соединение было разорвано")
                break
            if attempt >= ATTEMPTS_BEFORE_DELAY:
                await rf_writer(f"Нет соединения. Повторная попытка через {ATTEMPT_DELAY_SECS} сек.")
                await asyncio.sleep(ATTEMPT_DELAY_SECS)
                continue
            attempt += 1
            await rf_writer(f"Нет соединения. Повторная попытка.")

        finally:
            if all((reader, writer)):
                writer.close()
                await writer.wait_closed()
            await rf_writer("Соединение закрыто")


async def echo_client(host, port, log_file_descriptor=None):
    rf_writer = decorate_log_file_descriptor(log_file_descriptor)
    while True:
        async with open_connection(host, port, rf_writer) as rw:
            reader = rw[0]
            while True:
                row = await reader.readline()
                if not row:
                    break
                await rf_writer(f"{row.decode('utf8').strip()}")

        await asyncio.sleep(ATTEMPT_DELAY_SECS)


async def main():
    p = configargparse.ArgParser(default_config_files=['conf.ini'])
    p.add_argument('-u', '--host', help='host of the chat server', env_var='DVMN_HOST', default=SERVER_HOST)
    p.add_argument('-p', '--port', help='port of the chat server', env_var='DVMN_PORT', default=SERVER_PORT)
    p.add_argument('-f', '--filepath', help='path to the file where to store chat history',
                   env_var='DVMN_CHAT_PATH', default=DEFAULT_HISTORY_FILE)
    conf = p.parse_args()

    async with aiofiles.open(DEFAULT_HISTORY_FILE, 'a', buffering=1) as log_file:
        await asyncio.gather(echo_client(conf.host, conf.port, log_file))

if __name__ == '__main__':
    asyncio.run(main())
