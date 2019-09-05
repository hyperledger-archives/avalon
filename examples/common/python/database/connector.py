
import logging
import os

from shared_kv.remote_lmdb.lmdb_helper_proxy import LMDBHelperProxy
from shared_kv.shared_kv_interface import KvStorage

TCFHOME = os.environ.get("TCF_HOME", "/tmp")

logger = logging.getLogger(__name__)


def open(config):
    """
    @dev open implements a generic API for opening connections to a LMDB
        database where it's local or remote
    @return (conn, type), where
        - conn is the connection helper to interact with db
        - type is 1 for the local LMDB, 2 for the remote LMDB
    """

    kv_config = config.get('KvStorage')
    if kv_config is None:
        raise ValueError("config for KvStorage is missing")

    # employ the remote version if remote_url is set
    if kv_config.get("remote_url") is not None:
        database_url = kv_config["remote_url"]
        logger.info(f"connect to remote LMDB @{database_url}")
        return (LMDBHelperProxy(database_url), 2)

    # otherwise, use the local one
    storage_path = TCFHOME + '/' + kv_config['StoragePath']
    storage_size = kv_config['StorageSize']
    conn = KvStorage()
    if not conn.open(storage_path, storage_size):
        raise ValueError("Failed to open KV Storage DB")

    logger.info(f"employ the local LMDB @{storage_path}")
    return (conn, 1)
