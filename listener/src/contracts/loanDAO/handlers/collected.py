import web3
from contracts.event import EventHandler
from models import Commit
# import utils


class Collected(EventHandler):
    signature = "Collected(bytes32,uint256)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    # def _normalize(self):
    #     self._args["_id"] = utils.add_0x_prefix(self._args["_id"].hex())

    def handle(self):
        commit = Commit()

        commit.opcode = "collected_loanDAO"
        commit.timestamp = self._block_timestamp()
        commit.proof = self._transaction
      
        data = {
            "poolId": self._args.get("_poolId"),
            "amount": self._args.get("_amount")
        }


        commit.data = data

        return [commit]
