Chaino
======

Chaino is an EVM blockchain research tool to rapidly download blocks and issue calls against smart contracts.

`Github repository <https://github.com/0xidm/chaino>`_

Installation
------------

Python 3.9 is required.

.. code-block:: bash

   pip install 'git+https://github.com/0xidm/chaino'

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
