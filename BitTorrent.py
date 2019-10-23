import bencoder
import logging
log_file_name = 'ApplicationLog.log'


class Reader:
    def __init__(self, path):
        self.path = path
        self.announce = None
        self.announce_list = None
        self.info = None
        self.raw_file = None
        logging.basicConfig(filename=log_file_name, filemode='w')
        self.read()

    def read(self):
        with open(self.path, 'rb') as f:
            self.raw_file = bencoder.decode(f.read())

        try:
            self.announce = str(self.raw_file[b'announce'])[2:-1]
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

