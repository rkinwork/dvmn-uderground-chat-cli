import asyncio
import logging
import json
import re

import configargparse
from aiofiles.os import wrap as aiowrap

from utils import open_connection, decode_m
from utils import DEFAULT_SERVER_HOST, DEFAULT_SEND_SERVER_PORT

ESCAPE_MESSAGE_PATTERN = re.compile('\n+')


def setup_logging(debug_mode):
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)
    return aiowrap(logging.debug)


async def register(preferred_nickname, reader, writer, logger):
    await logger(decode_m(await reader.readline()))
    writer.write("\n".encode())
    await logger(decode_m(await reader.readline()))
    writer.write((preferred_nickname + "\n").encode())
    credentials = json.loads(await reader.readline())
    await logger(credentials)
    return credentials


async def authorise(token, reader, writer, logger):
    await logger(decode_m(await reader.readline()))
    writer.write(f"{token}\n".encode())
    response = json.loads(await reader.readline())
    if response is None:
        print("Unknown token. Check it, or register new user")
        return False
    await logger(response)
    return True


async def submit_message(message, reader, writer, logger):
    message = ESCAPE_MESSAGE_PATTERN.sub('\n', message)
    writer.write(f"{message}\n\n".encode())
    await logger(message)
    await logger(decode_m(await reader.readline()))
    print("Message has been sent successfully")


async def main():
    p = configargparse.ArgParser(default_config_files=['conf.ini'])
    p.add_argument('-u', '--host', help='host of the chat server', env_var='DVMN_HOST', default=DEFAULT_SERVER_HOST)
    p.add_argument('-p', '--port', help='port of the chat server', env_var='DVMN_SEND_PORT',
                   default=DEFAULT_SEND_SERVER_PORT)
    p.add_argument('-m', '--message', help='text of the message to send', required=True)
    p.add_argument('-d', '--debug', help='switch on debug mode', env_var='DVMN_DEBUG', action='store_true')
    group = p.add_mutually_exclusive_group()
    group.add_argument('-t', '--token', help='authorization token', env_var='DVMN_AUTH_TOKEN')
    group.add_argument('-n', '--nickname', help='name of the new user')
    conf = p.parse_args()

    logger = setup_logging(conf.debug)
    if conf.nickname:
        async with open_connection(DEFAULT_SERVER_HOST, DEFAULT_SEND_SERVER_PORT, logger) as rw:
            reader, writer = rw
            credentials = await register(conf.nickname, reader, writer, logger)
            if not credentials:
                print("Problems with new user registration. Try again later")
                return
            print(f"Save your token: {credentials['account_hash']}")
            conf.token = credentials['account_hash']

    async with open_connection(DEFAULT_SERVER_HOST, DEFAULT_SEND_SERVER_PORT, logger) as rw:
        reader, writer = rw
        if await authorise(conf.token, reader, writer, logger):
            await logger(decode_m(await reader.readline()))
            await submit_message(conf.message, reader, writer, logger)
        else:
            print("Problems with authorization. Check your token")


if __name__ == '__main__':
    asyncio.run(main())
