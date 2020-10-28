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


def decode_message(message):
    return message.decode('utf-8').strip()


@contextlib.asynccontextmanager
async def open_connection(server, port, message_writer):
    attempt = 0
    connected = False
    reader, writer = None, None
    while True:
        try:
            reader, writer = await asyncio.open_connection(server, port)
            await message_writer("Соединение установлено")
            connected = True
            yield reader, writer
            break

        except asyncio.CancelledError:
            raise

        except (ConnectionRefusedError, ConnectionResetError):
            if connected:
                await message_writer("Соединение было разорвано")
                break
            if attempt >= ATTEMPTS_BEFORE_DELAY:
                await message_writer(f"Нет соединения. Повторная попытка через {ATTEMPT_DELAY_SECS} сек.")
                await asyncio.sleep(ATTEMPT_DELAY_SECS)
                continue
            attempt += 1
            await message_writer(f"Нет соединения. Повторная попытка.")

        finally:
            if all((reader, writer)):
                writer.close()
                await writer.wait_closed()
            await message_writer("Соединение закрыто")
