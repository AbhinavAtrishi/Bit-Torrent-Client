# Temporary Python script to test the library functions. Will be deleted in the final versions.

from BitTorrent import Reader, Downloader

X = Reader('Lubuntu.torrent') # Put a torrent file here
X.get_peers()

D = Downloader(X.peer_list[0], X.port_list[0], X.info, X.info_sha1, X.piece_length, X.length)
D.main()
