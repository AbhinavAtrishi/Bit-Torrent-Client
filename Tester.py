# Temporary Python script to test the library functions. Will be deleted in the final versions.

from BitTorrent import Reader, Downloader

X = Reader('') # Put a torrent file here
X.get_peers()

print(X.response)

D = Downloader(X.peer_list[1], X.port_list[1], X.info, X.info_sha1)
D.handshake()