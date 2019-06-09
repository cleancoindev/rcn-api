import web3
from .event_handler import EventHandler
from handlers import utils


class ApprovalHandler(EventHandler):
    signature = 'Approval(address,address,uint256)'
    signature_hash = web3.Web3.sha3(text=signature)

    def _parse(self):
        data = self._event.get('data')[2:]
        splited_args = utils.split_every(64, data)

    def do(self):
        return []
