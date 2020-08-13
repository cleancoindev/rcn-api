import logging
import time
import json
import os
from ethereum_connection import EthereumConnection
from ethereum_connection import ContractConnection
from graceful.resources.generic import RetrieveAPI
from graceful.resources.generic import PaginatedListAPI
from graceful.parameters import StringParam
from graceful.parameters import BoolParam
from custom_parameters import SortingParam
from custom_validators import is_valid_sorting
import falcon
from serializers import DebtSerializer
from serializers import ConfigSerializer
from serializers import LoanSerializer
from serializers import StateSerializer
from serializers import CommitSerializer
from serializers import CollateralSerializer
from serializers import CompleteLoanSerializer
from serializers import ModelAndDebtSerializer
from models import Debt
from models import Config
from models import Loan
from models import State
from models import Commit
from models import Collateral
from models import Block
from clock import Clock
from utils import get_data
from utils import getBlock


URL_NODE = os.environ.get("URL_NODE")
eth_conn = EthereumConnection(URL_NODE)

logger = logging.getLogger(__name__)


class DebtList(PaginatedListAPI):
    serializer = DebtSerializer()

    error = BoolParam("Error filter")
    model = StringParam("Model filter")
    owner = StringParam("Owner filter")
    owner__ne = StringParam("owner not filter")
    model__ne = StringParam("Model not filter")
    creator = StringParam("Creator filter")
    creator__ne = StringParam("Creator not filter")
    oracle = StringParam("Oracle filter")
    oracle__ne = StringParam("Oracle not filter")

    balance__lt = StringParam("Balance lt")
    balance__lte = StringParam("Balance lte")
    balance__gt = StringParam("Balance gt")
    balance__gte = StringParam("Balance gte")

    created__lt = StringParam("Created lt")
    created__lte = StringParam("Created lt")
    created__gt = StringParam("Created gt")
    created__gte = StringParam("Created gte")

    def list(self, params, meta, **kwargs):
        # Filtering -> Ordering -> Limiting

        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        all_objects = Debt.objects.filter(**filter_params)
        count_objects = all_objects.count()
        meta["resource_count"] = count_objects
        meta["lastBlockPulled"] = Block.objects.first().number

        return all_objects.skip(offset).limit(page_size)


class DebtItem(RetrieveAPI):
    serializer = DebtSerializer()

    def retrieve(self, params, meta, id_debt, **kwargs):
        meta["lastBlockPulled"] = Block.objects.first().number
        try:
            return Debt.objects.get(id=id_debt)
        except Debt.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='Debt does not exists',
                description='Debt with id={} does not exists'.format(id_debt)
            )


class ConfigList(PaginatedListAPI):
    serializer = ConfigSerializer()

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        all_objects = Config.objects.filter(**filter_params)
        count_objects = all_objects.count()
        meta["resource_count"] = count_objects
        meta["lastBlockPulled"] = Block.objects.first().number

        return all_objects.skip(offset).limit(page_size)


class ConfigItem(RetrieveAPI):
    serializer = ConfigSerializer()

    def retrieve(self, params, meta, id_config, **kwargs):
        meta["lastBlockPulled"] = Block.objects.first().number
        try:
            return Config.objects.get(id=id_config)
        except Config.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='Config does not exists',
                description='Config with id={} does not exists'.format(id_config)
            )


class StateList(PaginatedListAPI):
    serializer = StateSerializer()

    status = StringParam("Status filter")

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        all_objects = State.objects.filter(**filter_params)
        count_objects = all_objects.count()
        meta["resource_count"] = count_objects
        meta["lastBlockPulled"] = Block.objects.first().number

        return all_objects.skip(offset).limit(page_size)


class StateItem(RetrieveAPI):
    serializer = StateSerializer()

    def retrieve(self, params, meta, id_state, **kwargs):
        meta["lastBlockPulled"] = Block.objects.first().number
        try:
            return State.objects.get(id=id_state)
        except State.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='State does not exists',
                description='State with id={} does not exists'.format(id_state)
            )


class CollateralList(PaginatedListAPI):
    serializer = CollateralSerializer()

    id = StringParam("Id filter")
    debt_id = StringParam("debt_id filter")
    token = StringParam("token filter")
    ##
    oracle = StringParam("oracle filter")
    liquidation_ratio = StringParam("liquidation_ratio filter")
    balance_ration = StringParam("balance_ration filter")
    burn_fee = StringParam("burn_fee filter")
    reward_fee = StringParam("reward_fee filter")
    amount = StringParam("amount filter")
    status = StringParam("status filter")

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        all_objects = Collateral.objects.filter(**filter_params)
        count_objects = all_objects.count()
        meta["resource_count"] = count_objects
        meta["lastBlockPulled"] = Block.objects.first().number

        return all_objects.skip(offset).limit(page_size)


class CollateralItem(RetrieveAPI):
    serializer = CollateralSerializer()

    def retrieve(self, params, meta, id_collateral, **kwargs):
        meta["lastBlockPulled"] = Block.objects.first().number
        try:
            collateral = Collateral.objects.get(id=id_collateral)

            return collateral
        except Collateral.DoesNotExist:
            raise falcon.HTTPNotFound(
                title='Collateral does not exists',
                description='Collateral with id={} does not exists'.format(id_collateral)
            )


class LoanList(PaginatedListAPI):
    serializer = LoanSerializer()

    open = BoolParam("Open filter")
    approved = BoolParam("Approved filter")
    cosigner = StringParam("Cosigner filter")
    cosigner__ne = StringParam("Cosigner not filter")
    model = StringParam("Model filter")
    model__ne = StringParam("Model not filter")
    creator = StringParam("Creator filter")
    creator__ne = StringParam("Creator not filter")
    oracle = StringParam("Oracle filter")
    oracle__ne = StringParam("Oracle not filter")
    borrower = StringParam("Borrower filter")
    borrower__ne = StringParam("Borrower not filter")
    callback = StringParam("Callback filter")
    canceled = BoolParam("Canceled filter")
    status = StringParam("Status Filter")
    currency = StringParam("Currency filter")
    currency__ne = StringParam("Currency not filter")

    expiration__lt = StringParam("Expiration lt")
    expiration__lte = StringParam("Expiration lte")
    expiration__gt = StringParam("Expiration gt")
    expiration__gte = StringParam("Expiration gte")

    amount__lt = StringParam("Amount lt")
    amount__lte = StringParam("Amount lte")
    amount__gt = StringParam("Amount gt")
    amount__gte = StringParam("Amount gte")

    created__lt = StringParam("Created lt")
    created__lte = StringParam("Created lte")
    created__gt = StringParam("Created gt")
    created__gte = StringParam("Created gte")


    def list(self, params, meta, **kwargs):
        # Filtering -> Ordering -> Limiting
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        all_objects = Loan.objects.filter(**filter_params)
        count_objects = all_objects.count()
        meta["resource_count"] = count_objects
        meta["lastBlockPulled"] = Block.objects.first().number

        return all_objects.skip(offset).limit(page_size)


class LoanItem(RetrieveAPI):
    serializer = LoanSerializer()

    def retrieve(self, params, meta, id_loan, **kwargs):
        meta["lastBlockPulled"] = Block.objects.first().number
        try:
            return Loan.objects.get(id=id_loan)
        except Loan.DoesNotExist:
            raise falcon.HTTPNotFound(
                title="Loan does not exists",
                description="Loan with id={} does not exists".format(id_loan)
            )


class CommitList(PaginatedListAPI):
    serializer = CommitSerializer()

    id_loan = StringParam("id_loan filter")
    opcode = StringParam("opcode filter")
    proof = StringParam("proof filter")
    address = StringParam("address filter")

    def list(self, params, meta, **kwargs):
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        all_objects = Commit.objects.filter(**filter_params)
        count_objects = all_objects.count()
        meta["resource_count"] = count_objects
        meta["lastBlockPulled"] = Block.objects.first().number

        return all_objects.skip(offset).limit(page_size)


class HealthStatusResource(object):
    def on_get(self, req, resp):
        clock = Clock()
        now = int(time.time())
        lower_limit = 60 * 2  # 2 minutes
        resp.status = falcon.HTTP_503
        is_sync = now - clock.time < lower_limit
        if is_sync:
            resp.status = falcon.HTTP_200


class LivenessProbe(object):
    def on_get(self, req, resp):
        last_block_pulled = int(Block.objects.first().number)
        # last_block = eth_conn.w3.eth.getBlock("latest").get("number")
        last_block = getBlock(eth_conn.w3, "latest").get("number")
        body = {
            "last_block_pulled": str(last_block_pulled),
            "last_block": str(last_block)
        }

        resp.body = json.dumps(body)
        resp.status = falcon.HTTP_200

        if last_block_pulled + 5 <= last_block:
            resp.status = falcon.HTTP_503


class ReadinessProbe(object):
    def on_get(self, req, resp):
        body = {
            "last_block_pulled": Block.objects.first().number,
            "last_block": str(getBlock(eth_conn.w3, "latest").get("number"))
        }
        resp.body = json.dumps(body)
        resp.status = falcon.HTTP_503

        if body.get("last_block_pulled") == body.get("last_block"):
            resp.status = falcon.HTTP_200


class ModelAndDebtDataResource(RetrieveAPI):

    serializer = ModelAndDebtSerializer()

    def retrieve(self, params, meta, id_loan, **kwargs):

        meta["lastBlockPulled"] = Block.objects.first().number
        try:
            data = get_data(id_loan)
            return data
        except Debt.DoesNotExist:
            raise falcon.HTTPNotFound(
                title="Debt does not exist",
                description="Debt with id={} does not exist".format(id_loan)
            )
        except Exception:
            raise falcon.HTTPNotFound(
                title="Error",
                description="An error ocurred :(".format(id_loan)
            )


class ConfigInfo(object):
    def on_get(self, req, resp):
        data = {
            "addresses": {
                "loan_manager": os.environ.get("LOAN_MANAGER_ADDRESS"),
                "debt_engine": os.environ.get("DEBT_ENGINE_ADDRESS"),
                "installments": os.environ.get("INSTALLMENTS_ADDRESS"),
                "collateral": os.environ.get("COLLATERAL_ADDRESS")
            }
        }

        resp.body = json.dumps(data)
        resp.status = falcon.HTTP_200


class CompleteLoanItem(RetrieveAPI):
    serializer = CompleteLoanSerializer()

    def retrieve(self, params, meta, id_loan, **kwargs):
        try:
            meta["lastBlockPulled"] = Block.objects.first().number

            complete_loan = Loan.objects.aggregate(
                [
                    { "$match": { "_id": id_loan}},
                    {"$lookup": {"from": "debt", "localField": "_id", "foreignField": "_id", "as": "debt"}},
                    {"$lookup": {"from": "config", "localField": "_id", "foreignField": "_id", "as": "config"}},
                    {"$lookup": {"from": "state", "localField": "_id", "foreignField": "_id", "as": "state"}},
                    {"$lookup": {"from": "collateral", "localField": "_id", "foreignField": "debt_id", "as": "collaterals"}},
                    { "$unwind": { "path": "$debt", "preserveNullAndEmptyArrays": True }},
                    { "$unwind": { "path": "$state", "preserveNullAndEmptyArrays": True }},
                    { "$unwind": { "path": "$config", "preserveNullAndEmptyArrays": True }},
                    { "$project": {
                        "id": 1,
                        "open": 1,
                        "approved": 1,
                        "position": 1,
                        "expiration": 1,
                        "amount": 1,
                        "cosigner": 1,
                        "model": 1,
                        "creator": 1,
                        "oracle": 1,
                        "borrower": 1,
                        "callback": 1,
                        "salt": 1,
                        "loanData": 1,
                        "created": 1,
                        "descriptor": 1,
                        "currency": 1,
                        "status": 1,
                        "canceled": 1,
                        "debt": 1,
                        "state": 1,
                        "collaterals": 1,
                        "config": "$config.data", "id": 1, "open": 1
                        }
                    }
                ]
            )
            list_query = list(complete_loan)
            if list_query:
                return list_query[0]
            else:
                raise falcon.HTTPNotFound(
                    title="Loan does not exists",
                    description="Loan with id={} does not exists".format(id_loan)
                )

            
        except Loan.DoesNotExist:
            raise falcon.HTTPNotFound(
                title="Loan does not exists",
                description="Loan with id={} does not exists".format(id_loan)
            )


class CompleteLoanList(PaginatedListAPI):
    serializer = CompleteLoanSerializer()

    open = BoolParam("Open filter")
    approved = BoolParam("Approved filter")
    cosigner = StringParam("Cosigner filter")
    cosigner__ne = StringParam("Cosigner not filter")
    model = StringParam("Model filter")
    model__ne = StringParam("Model not filter")
    creator = StringParam("Creator filter")
    creator__ne = StringParam("Creator not filter")
    oracle = StringParam("Oracle filter")
    oracle__ne = StringParam("Oracle not filter")
    borrower = StringParam("Borrower filter")
    borrower__ne = StringParam("Borrower not filter")
    callback = StringParam("Callback filter")
    canceled = BoolParam("Canceled filter")
    status = StringParam("Status Filter")
    currency = StringParam("Currency filter")
    currency__ne = StringParam("Currency not filter")
    owner = StringParam("Owner filter")

    expiration__lt = StringParam("Expiration lt")
    expiration__lte = StringParam("Expiration lte")
    expiration__gt = StringParam("Expiration gt")
    expiration__gte = StringParam("Expiration gte")

    amount__lt = StringParam("Amount lt")
    amount__lte = StringParam("Amount lte")
    amount__gt = StringParam("Amount gt")
    amount__gte = StringParam("Amount gte")

    created__lt = StringParam("Created lt")
    created__lte = StringParam("Created lte")
    created__gt = StringParam("Created gt")
    created__gte = StringParam("Created gte")

    def list(self, params, meta, **kwargs):
        # Filtering -> Ordering -> Limiting
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        if "owner" in filter_params:
            meta["lastBlockPulled"] = Block.objects.first().number
            
            owner_filter = filter_params.pop("owner")
            all_objects = Loan.objects.filter(**filter_params)


            query_result = all_objects.aggregate(
                [
                    {"$lookup": {"from": "debt", "localField": "_id", "foreignField": "_id", "as": "debt"}},
                    { "$match": {"debt.owner": owner_filter}},
                    {"$lookup": {"from": "config", "localField": "_id", "foreignField": "_id", "as": "config"}},
                    {"$lookup": {"from": "state", "localField": "_id", "foreignField": "_id", "as": "state"}},
                    {"$lookup": {"from": "collateral", "localField": "_id", "foreignField": "debt_id", "as": "collaterals"}},
                    { "$unwind": { "path": "$debt", "preserveNullAndEmptyArrays": True }},
                    { "$unwind": { "path": "$state", "preserveNullAndEmptyArrays": True }},
                    { "$unwind": { "path": "$config", "preserveNullAndEmptyArrays": True }},
                    { "$sort": {"created": -1} },
                    { "$facet": {
                        "resources": [
                            { "$skip": offset },
                            { "$limit": page_size},
                            { "$project": {
                                "id": 1,
                                "open": 1,
                                "approved": 1,
                                "position": 1,
                                "expiration": 1,
                                "amount": 1,
                                "cosigner": 1,
                                "model": 1,
                                "creator": 1,
                                "oracle": 1,
                                "borrower": 1,
                                "callback": 1,
                                "salt": 1,
                                "loanData": 1,
                                "created": 1,
                                "descriptor": 1,
                                "currency": 1,
                                "status": 1,
                                "canceled": 1,
                                "debt": 1,
                                "state": 1,
                                "collaterals": 1,
                                "config": "$config.data", "id": 1, "open": 1
                                }
                            }
                        ],
                        "resource_count": [{"$count": "debt"}]
                    }
                    }
                ]
            )
            list_query_result = list(query_result)
            if list_query_result:
                list_complete_loans = list_query_result[0]
            else:
                raise falcon.HTTPNotFound(
                    title="Loan does not exists",
                    description="Loan with id={} does not exists".format(id_loan)
                )

            resources = list_complete_loans.get("resources")
            resource_count = list_complete_loans.get("resource_count")

            if resource_count:
                meta["resource_count"] = resource_count[0].get("debt")
            else:
                meta["resource_count"] = 0
            return resources

        else:
            all_objects = Loan.objects.filter(**filter_params)
            count_objects = all_objects.count()
            meta["resource_count"] = count_objects
            meta["lastBlockPulled"] = Block.objects.first().number

            # loan_filtered = all_objects.skip(offset).limit(page_size)
            query = [
                    {"$lookup": {"from": "debt", "localField": "_id", "foreignField": "_id", "as": "debt"}},
                    {"$lookup": {"from": "config", "localField": "_id", "foreignField": "_id", "as": "config"}},
                    {"$lookup": {"from": "state", "localField": "_id", "foreignField": "_id", "as": "state"}},
                    {"$lookup": {"from": "collateral", "localField": "_id", "foreignField": "debt_id", "as": "collaterals"}},
                    { "$unwind": { "path": "$debt", "preserveNullAndEmptyArrays": True }},
                    { "$unwind": { "path": "$state", "preserveNullAndEmptyArrays": True }},
                    { "$unwind": { "path": "$config", "preserveNullAndEmptyArrays": True }},
                    { "$sort": {"created": -1} },
                    { "$skip": offset },
                    { "$limit": page_size},
                    { "$project": {
                        "id": 1,
                        "open": 1,
                        "approved": 1,
                        "position": 1,
                        "expiration": 1,
                        "amount": 1,
                        "cosigner": 1,
                        "model": 1,
                        "creator": 1,
                        "oracle": 1,
                        "borrower": 1,
                        "callback": 1,
                        "salt": 1,
                        "loanData": 1,
                        "created": 1,
                        "descriptor": 1,
                        "currency": 1,
                        "status": 1,
                        "canceled": 1,
                        "debt": 1,
                        "state": 1,
                        "collaterals": 1,
                        "config": "$config.data", "id": 1, "open": 1
                        }
                    }
                ]

            #print(query)
            complete_loans = all_objects.aggregate(query)

            return list(complete_loans)


class CompleteLoanList2(PaginatedListAPI):
    serializer = CompleteLoanSerializer()

    open = BoolParam("Open filter")
    approved = BoolParam("Approved filter")
    cosigner = StringParam("Cosigner filter")
    cosigner__ne = StringParam("Cosigner not filter")
    model = StringParam("Model filter")
    model__ne = StringParam("Model not filter")
    creator = StringParam("Creator filter")
    creator__ne = StringParam("Creator not filter")
    oracle = StringParam("Oracle filter")
    oracle__ne = StringParam("Oracle not filter")
    borrower = StringParam("Borrower filter")
    borrower__ne = StringParam("Borrower not filter")
    callback = StringParam("Callback filter")
    canceled = BoolParam("Canceled filter")
    status = StringParam("Status Filter")
    currency = StringParam("Currency filter")
    currency__ne = StringParam("Currency not filter")
    owner = StringParam("Owner filter")

    expiration__lt = StringParam("Expiration lt")
    expiration__lte = StringParam("Expiration lte")
    expiration__gt = StringParam("Expiration gt")
    expiration__gte = StringParam("Expiration gte")

    amount__lt = StringParam("Amount lt")
    amount__lte = StringParam("Amount lte")
    amount__gt = StringParam("Amount gt")
    amount__gte = StringParam("Amount gte")

    created__lt = StringParam("Created lt")
    created__lte = StringParam("Created lte")
    created__gt = StringParam("Created gt")
    created__gte = StringParam("Created gte")

    order_by = SortingParam("Order by", validators=[is_valid_sorting])

    def list(self, params, meta, **kwargs):
        # Filtering -> Ordering -> Limiting
        filter_params = params.copy()
        filter_params.pop("indent")

        page_size = filter_params.pop("page_size")
        page = filter_params.pop("page")

        offset = page * page_size

        meta["lastBlockPulled"] = Block.objects.first().number

        owner_filter = filter_params.pop("owner", None)
        order_by = filter_params.pop("order_by", {"field": "created", "type": "desc"})

        order_by_field = order_by["field"]
        if order_by["type"] == "asc":
            order_by_type = 1
        elif order_by["type"] == "desc":
            order_by_type = -1


        all_objects = Loan.objects.filter(**filter_params)

        # Build the query
        query = []

        lookup_debt = {"$lookup": {"from": "debt", "localField": "_id", "foreignField": "_id", "as": "debt"}}
        match_owner = {"$match": {"debt.owner": owner_filter}} if owner_filter is not None else None
        lookup_config = {"$lookup": {"from": "config", "localField": "_id", "foreignField": "_id", "as": "config"}}
        lookup_state = {"$lookup": {"from": "state", "localField": "_id", "foreignField": "_id", "as": "state"}}
        lookup_collateral = {"$lookup": {"from": "collateral", "localField": "_id", "foreignField": "debt_id", "as": "collaterals"}}
        unwind_debt = {"$unwind": {"path": "$debt", "preserveNullAndEmptyArrays": True}}
        unwind_state = {"$unwind": {"path": "$state", "preserveNullAndEmptyArrays": True}}
        unwind_config = {"$unwind": {"path": "$config", "preserveNullAndEmptyArrays": True}}
        # sorting = {"$sort": {"created": -1}}
        sorting = {"$sort": {order_by_field: order_by_type}}
        facet = { "$facet": {
                        "resources": [
                            { "$skip": offset },
                            { "$limit": page_size},
                            { "$project": {
                                "id": 1,
                                "open": 1,
                                "approved": 1,
                                "position": 1,
                                "expiration": 1,
                                "amount": 1,
                                "cosigner": 1,
                                "model": 1,
                                "creator": 1,
                                "oracle": 1,
                                "borrower": 1,
                                "callback": 1,
                                "salt": 1,
                                "loanData": 1,
                                "created": 1,
                                "descriptor": 1,
                                "currency": 1,
                                "status": 1,
                                "canceled": 1,
                                "debt": 1,
                                "state": 1,
                                "collaterals": 1,
                                "config": "$config.data", "id": 1, "open": 1
                                }
                            }
                        ],
                        "resource_count": [{"$count": "debt"}]
                    }
                }

        
        query.append(lookup_debt)
        if match_owner:
            query.append(match_owner)
        query.append(lookup_config)
        query.append(lookup_state)
        query.append(lookup_collateral)
        query.append(unwind_debt)
        query.append(unwind_state)
        query.append(unwind_config)
        query.append(sorting)
        query.append(facet)

        print(query)

        query_result = all_objects.aggregate(query)

        list_query_result = list(query_result)
        if list_query_result:
            list_complete_loans = list_query_result[0]
        else:
            raise falcon.HTTPNotFound(
                title="Loan does not exists",
                description="Loan with id={} does not exists".format(id_loan)
            )

        resources = list_complete_loans.get("resources")
        resource_count = list_complete_loans.get("resource_count")

        if resource_count:
            meta["resource_count"] = resource_count[0].get("debt")
        else:
            meta["resource_count"] = 0
        return resources
