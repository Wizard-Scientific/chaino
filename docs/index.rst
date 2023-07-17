Chaino
======

Chaino is an EVM blockchain research tool to rapidly download blocks and issue calls against smart contracts.

`Github repository <https://github.com/0xidm/chaino>`_

Installation
------------

Python 3.9 is required.

.. code-block:: bash

   pip install 'git+https://github.com/0xidm/chaino'

Python example: Block download
------------------------------

Download the first 1000 blocks of the Fantom DAG with `BlockScheduler <BlockScheduler_>`_.

.. code-block:: python

   from chaino.scheduler.block import BlockScheduler
   from chaino.rpc import RPC

   scheduler = BlockScheduler(filestore_path="/tmp/chaino-example")
   scheduler.add_rpc(RPC(url="https://rpc.ftm.tools"))
   for block_number in range(1, 1000):
      scheduler.add_task(block_number=block_number)
   scheduler.start()

Results will be available as a `NestedFilestore <NestedFilestore_>`_ in `/tmp/chaino-example`.

Python example: Calling contract functions
------------------------------------------

Get ERC-20 balances for a list of addresses on Fantom with `CallScheduler <CallScheduler_>`_

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

On the command line, download the first 1000 blocks of the Fantom DAG.
Then, extract all transactions and write them to a CSV file.

.. code-block:: bash

   mkdir -p var
   blockchain.py download fantom 1 1000 var/fantom
   blockchain.py transactions-csv 1 1000 var/fantom > var/fantom-txs.csv

API
===

BlockScheduler
--------------

.. autoclass:: chaino.scheduler.block.BlockScheduler
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

CallScheduler
-------------

.. autoclass:: chaino.scheduler.call.CallScheduler
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Scheduler
---------

.. autoclass:: chaino.scheduler.Scheduler
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

RPC
---

.. autoclass:: chaino.rpc.RPC
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

NestedFilestore
---------------

.. autoclass:: chaino.nested_filestore.NestedFilestore
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

GroupedMulticall
----------------

.. autoclass:: chaino.grouped_multicall.GroupedMulticall
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
