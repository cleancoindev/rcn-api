import web3
from contracts.event import EventHandler
from models import Commit
import utils


class Error(EventHandler):
    signature = "Error(bytes32,address,uint256,uint256,uint256,bytes)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    def _normalize(self):
        self._args["_id"] = utils.add_0x_prefix(self._args["_id"].hex())

    def handle(self):
        commit = Commit()

        commit.opcode = "error_debt_engine"
        commit.timestamp = self._block_timestamp()
        commit.proof = self._transaction
        commit.address = self._tx.get("from")

        data = {
            "id": self._args.get("_id"),
            "error": True
        }

        commit.id_loan = self._args.get("_id")
        commit.data = data

        return [commit]
