import sys
import contextlib
import datetime

import asyncio
from aiofiles.os import wrap as aiowrap

DEFAULT_LOG_DESCRIPTOR = aiowrap(sys.stdout.write)
LOG_DTTM_TMPL = '%d-%m-%y %H:%M:%S'
ATTEMPT_DELAY_SECS = 3
ATTEMPTS_BEFORE_DELAY = 2
DEFAULT_SERVER_HOST = 'minechat.dvmn.org'
DEFAULT_LISTEN_SERVER_PORT = 5000
DEFAULT_SEND_SERVER_PORT = 5050
DEFAULT_HISTORY_FILE = 'minechat.history'


def decode_m(message):
    return message.decode('utf-8').strip()


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
