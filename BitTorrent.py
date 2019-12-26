import bencoder
import logging
import requests
import hashlib
import random
import socket
import struct
import asyncio
from tqdm import tqdm
log_file_name = 'ApplicationLog.log'
version = '000'
random.seed(90)
sys_id = ''.join(str(random.randint(0, 9)) for _ in range(12))
my_id = ('-SBC'+version+'-'+sys_id).encode('ascii')


class Reader:
    def __init__(self, path):
        self.path = path
        self.announce = None
        self.announce_list = None
        self.info = None
        self.raw_file = None
        self.info_sha1 = None
        self.my_id = my_id
        self.total_file_size = 0
        self.response = None
        self.url_params = None
        self.peer_list = None
        self.port_list = None
        self.piece_length = None
        self.length = None
        logging.basicConfig(filename=log_file_name, filemode='w')
        self.read()
        self.compute_sha()
        self.compute_size()

    def read(self):
        with open(self.path, 'rb') as f:
            self.raw_file = bencoder.decode(f.read())

        try:
            self.announce = self.raw_file[b'announce']
        except Exception as e:
            logging.warning(f'In {self.__class__.__name__}: Announce URL not found', exc_info=e)

        try:
            self.announce_list = self.raw_file[b'announce-list']
        except Exception as e:
            logging.warning(f'In {self.__class__.__name__}: Announce List not found', exc_info=e)

        try:
            self.info = self.raw_file[b'info']
        except Exception as e:
            logging.warning(f'In {self.__class__.__name__}: Info not found', exc_info=e)

        self.piece_length = self.info[b'piece length']
        self.length = self.info[b'length']

    def compute_sha(self):
        self.info_sha1 = hashlib.sha1(bencoder.encode(self.info)).digest()

    def compute_size(self):
        try:
            for file in self.info[b'files']:
                self.total_file_size += file[b'length']
        except Exception as e:
            logging.warning('Single File found, no multiple files', exc_info=e)
            self.total_file_size += self.info[b'length']

    def get_peers(self):
        self.url_params = {'info_hash': self.info_sha1, 'peer_id': self.my_id, 'port': 6881, 'uploaded': 0,
                           'downloaded': 0, 'left': self.total_file_size, 'event': 'started', 'compact': 1}

        response = requests.get(self.announce.decode('ascii'), params=self.url_params)

        self.response = bencoder.decode(response.content)

        peers = self.response[b'peers']
        peer_list = []
        port_list = []
        for itr in range(0, len(peers), 6):
            out_tup = struct.unpack('>BBBBH', peers[itr:itr+6])
            peer_ip = str(out_tup[0]) + '.' + str(out_tup[1]) + '.' + str(out_tup[2]) + '.' + str(out_tup[3])
            peer_list.append(peer_ip)
            port_list.append(out_tup[4])

        self.peer_list = peer_list
        self.port_list = port_list


# Downloader Class performs the handshake to peers & will then proceed to establish connection, request for pieces.
class Downloader:
    def __init__(self, peer_ip, peer_port, info, info_sha1, piece_length, length):
        self.peer_ip = peer_ip
        self.peer_id = None
        self.peer_port = peer_port
        self.info = info
        self.info_sha1 = info_sha1
        self.piece_length = piece_length
        self.length = length
        self.my_id = my_id
        self.reserved = chr(0) * 8
        self.pstrlen = 19
        self.pstr = 'BitTorrent protocol'
        self.Choked = True

    def choked_state(self, sock):
        msg_interested = struct.pack('>Ib', 1, 2)
        msg_unchoke = struct.pack('>Ib', 1, 1)
        msg_len = len(msg_interested)

        # sock.connect((self.peer_ip, self.peer_port))
        sock.sendall(msg_interested)
        recv = sock.recv(msg_len)
        while recv != msg_unchoke:
            recv = sock.recv(msg_len)

        print("Unchoked !")
        return True

    def handshake(self, sock):
        handshake_message = ((chr(19)).encode('ascii') + b'BitTorrent protocol' +
                             self.reserved.encode('ascii') + self.info_sha1 + self.my_id)

        # sock.connect((self.peer_ip, self.peer_port))
        sock.sendall(handshake_message)
        reply = sock.recv(len(handshake_message))
        sha_recv = reply[28:48]
        self.peer_id = reply[48:]

        if sha_recv == self.info_sha1:
            return True
        return False

    def _download(self, sock):
        '''Incomplete code under development. DO NOT USE!!'''
        request_size = 2 ** 14
        max_subparts = round(self.piece_length / request_size)
        num_pieces = round(self.length / self.piece_length)

        for piece_current in range(num_pieces):
            for subpart in tqdm(range(max_subparts)):
                offset = request_size * subpart
                msg = struct.pack('>IbIII', 13, 6, piece_current, offset, request_size)
                sock.sendall(msg)
                data_recv = sock.recv(request_size)
                print("Data Recvd : ", data_recv)
            break

    def main(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.peer_ip, self.peer_port))
            print(f'Handshake: {self.handshake(s)}')
            print(f'Unchoked {self.choked_state(s)}')
            self._download(s)















