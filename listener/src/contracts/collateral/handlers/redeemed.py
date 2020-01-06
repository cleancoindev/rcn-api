import web3
from contracts.event import EventHandler
from models import Commit


class Redeemed(EventHandler):
    signature = "Redeemed(uint256)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    def handle(self):
        commit = Commit()

        commit.opcode = "redeemed_collateral"
        commit.timestamp = self._block_timestamp()
        commit.proof = self._transaction
        commit.address = self._tx.get("from")

        data = {
            "id": str(self._args.get("_entryId")),
            "status": str(CollateralState.TO_WITHDRAW.value)
        }

        commit.data = data

        return [commit]
