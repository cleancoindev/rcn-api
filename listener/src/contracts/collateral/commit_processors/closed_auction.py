from contracts.commit_processor import CommitProcessor


class ClosedAuction(CommitProcessor):
    def __init__(self):
        self.opcode = "closed_auction"

    def process(self, commit, *args, **kwargs):
        data = commit.data

        collateral = Collateral.objects.get(id=data["id"])

        collateral.status = data.get("status")
        collateral.amount = data.get("leftover")

        collateral.save()
        commit.save()
