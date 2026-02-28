# Copyright (c) 2021-2024 doronz <doron88@gmail.com>
# Linux TUN backend using pytun_pmd3 (replaces macOS utunuds)
import asyncio
import logging
import struct
import subprocess
import sys

from socket import AF_INET6
from typing import Callable

from pytun_pmd3 import TunTapDevice

IPV6_HEADER_SIZE = 40

if sys.platform == 'darwin':
    UTUN_INET6_HEADER = struct.pack('>I', AF_INET6)
else:
    UTUN_INET6_HEADER = b'\x00\x00\x86\xdd'

UTUN_INET6_HEADER_SIZE = len(UTUN_INET6_HEADER)

logger = logging.getLogger(__name__)


class ExternalUtun:
    def __init__(self):
        self.tun = None
        self.name = ""
        self._read_task = None
        self.callback = None

    def write(self, data):
        if self.tun is not None:
            self.tun.write(data)

    async def up(
        self,
        label: str,
        ipv6: str,
        incoming_data_callback: Callable,
    ) -> str:
        self.callback = incoming_data_callback
        self.tun = TunTapDevice()
        self.name = self.tun.name

        # Configure via ip commands (more reliable than ioctl for IPv6 on TUN)
        subprocess.run(
            ['ip', '-6', 'addr', 'add', f'{ipv6}/64', 'dev', self.name],
            check=True,
        )
        subprocess.run(
            ['ip', 'link', 'set', self.name, 'up'],
            check=True,
        )
        logger.debug('TUN %s up with %s/64', self.name, ipv6)

        self._read_task = asyncio.create_task(
            self._tun_read_task(), name=f'tun-read-{label}'
        )
        return self.name

    async def _tun_read_task(self):
        """Read IPv6 frames from TUN fd and dispatch via callback."""
        loop = asyncio.get_event_loop()
        while True:
            data = await loop.run_in_executor(None, self.tun.read, 65535)
            if not data:
                break
            if not data.startswith(UTUN_INET6_HEADER):
                continue
            await self.callback(data)

    def down(self) -> None:
        if self._read_task:
            self._read_task.cancel()
            self._read_task = None
        if self.tun:
            self.tun.close()
            self.tun = None

    def __del__(self):
        self.down()
