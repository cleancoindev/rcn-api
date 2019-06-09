import web3
from .event_handler import EventHandler
from handlers import utils
from models import Commit

class DestroyedByHandler(EventHandler):
    signature = 'DestroyedBy(uint256,address)'
    signature_hash = web3.Web3.sha3(text=signature)

    def _parse(self):
        data = self._event.get('data')[2:]
        splited_args = utils.split_every(64, data)
        self._index = utils.to_int(splited_args[0])
        self._address = utils.to_address(splited_args[1])
        self._block_number = self._event.get('blockNumber')
        self._transaction = self._event.get('transactionHash').hex()

    def do(self):
        commit = Commit()

        data = {}
        data['loan'] = self._index
        data['destroyed_by'] = self._address

        commit.opcode = "destroyed_loan"
        commit.timestamp = str(self._w3.eth.getBlock(self._block_number).timestamp)
        commit.proof = self._transaction
        commit.data = data
        commit.id_loan = self._index

        return [commit]
