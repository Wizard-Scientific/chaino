Chaino
======

Chaino is an EVM blockchain research tool to rapidly:

- `download blocks <https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_getblockbynumber>`_ from an EVM blockchain
- `issue calls <https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_call>`_ against smart contracts

Overview
--------

Chaino can use `multiple RPCs <https://chainlist.org/>`_ in parallel, each with multiple threads.
Chaino attempts to automatically maximize its speed without abusing the RPC.

Blocks are stored as `web3.py <https://web3py.readthedocs.io/en/v5/web3.eth.html>`_ objects inside `Python pickle <https://docs.python.org/3/library/pickle.html>`_ files.
The block files are archived with `NestedFilestore <https://github.com/0xidm/nested-filestore>`, which can manage millions of files on a filesystem.

Calls are bundled with `GroupedMulticall <https://chaino.readthedocs.io/en/latest/#groupedmulticall>`_, which is a wrapper around `Multicall <https://github.com/banteg/multicall.py>`_.
A GroupedMulticall can be executed against the current head block or any historical block, as the RPC permits.

Installation
------------

Python 3.9 is required.

.. code-block:: bash

   pip install 'git+https://github.com/0xidm/chaino'

Online resources
----------------

- `Github repository <https://github.com/0xidm/chaino>`_
- `Documentation <https://chaino.readthedocs.org>`_

Usage
=====

Python example: Block download with BlockScheduler
--------------------------------------------------

Download the first 1000 blocks of the Fantom DAG with `BlockScheduler <https://chaino.readthedocs.io/en/latest/#blockscheduler>`_.

.. code-block:: python

   from chaino.scheduler.block import BlockScheduler
   from chaino.rpc import RPC

   scheduler = BlockScheduler(filestore_path="chaino-example")
   scheduler.add_rpc(RPC(url="https://rpc.ftm.tools"))
   for block_number in range(1, 1000):
      scheduler.add_task(block_number=block_number)
   scheduler.start()

Results will be available as a ``NestedFilestore`` in a directory called ``chaino-example``.

Python example: Calling contract functions with CallScheduler
--------------------------------------------------------------

Get ERC-20 balances for a list of addresses on Fantom with `CallScheduler <https://chaino.readthedocs.io/en/latest/#callscheduler>`_

.. code-block:: python

   from chaino.scheduler.call import CallScheduler, parse_address
   from chaino.rpc import RPC

   result = CallScheduler.map_call(
      rpc=RPC(url="https://rpc.ftm.tools"),
      contract_address="0x21Ada0D2aC28C3A5Fa3cD2eE30882dA8812279B6",
      function_signature="balanceOf(address)(uint256)",
      inputs=[
         ["0x5aa1039D09330DF607F88e72bb9C1E0F66C96AA0"],
         ["0x18Bf8D51f7695AA3E63fEA9E99416530c1420511"],
      ]
   )
   [(parse_address(key), value) for key, value in result.items()]

which produces these results:

.. code-block:: python

   [('0x5aa1039D09330DF607F88e72bb9C1E0F66C96AA0', 5925106268789833088835427),
   ('0x18Bf8D51f7695AA3E63fEA9E99416530c1420511', 2765360879676247594525586)]

Command Line Example
--------------------

The example script ``blockchain.py`` demonstrates some simple chaino tasks.

On the command line, download the first 1000 Arbitrum blocks.
Then, extract all transactions as CSV to a separate filestore.
Finally, combine all transactions into a single CSV file.

.. code-block:: bash

   mkdir -p var
   blockchain.py download arbitrum 1 1000 var/arbitrum-blocks
   blockchain.py extract-txs var/arbitrum-blocks var/arbitrum-txs 3,3
   blockchain.py transactions-csv var/arbitrum-txs 3,3 ./var/arbitrum-txs.csv.gz

Docker
------

Chaino can also run in a Docker container.

.. code-block:: bash

   docker build -t chaino https://raw.githubusercontent.com/0xidm/chaino/main/Dockerfile
   docker volume create chaino
   docker run --rm -it --name chaino -v chaino:/mnt/chaino chaino

To provide a custom RPC configuration file, add another ``-v`` option:

.. code-block:: bash

   docker run --rm -it --name chaino -v chaino:/mnt/chaino -v /path/to/rpc.json:/home/chaino/.config/chaino/rpc.json chaino

To monitor progress inside a chaino container:

.. code-block:: bash

   docker exec -it chaino tail -f /tmp/chaino.log
