import web3
from contracts.event import EventHandler
from models import Commit
import utils


class ErrorRecover(EventHandler):
    signature = "ErrorRecover(bytes32,address,uint256,uint256,uint256,bytes32,bytes)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    def _normalize(self):
        self._args["_id"] = utils.add_0x_prefix(self._args["_id"].hex())

    def handle(self):
        commit = Commit()

        commit.opcode = "error_recover_debt_engine"
        commit.timestamp = self._block_timestamp()
        commit.proof = self._transaction
        commit.address = self._tx.get("from") if not self._tx is None else None

        data = {
            "id": self._args.get("_id"),
            "error": False
        }

        commit.id_loan = self._args.get("_id")
        commit.data = data

        return [commit]
