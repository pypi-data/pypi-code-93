# coding=utf-8
# pylint: disable=eval-used
import json
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import marshal_with
from rest_server.resource.models.helper import resource_fields
from test_framework.test_pool import TestPool
from test_framework.state import State
from test_framework.state import TestType


PARSER = reqparse.RequestParser()
PARSER.add_argument('parameters')
PARSER.add_argument('mode')
PARSER.add_argument('key')


class BenchmarkResource(Resource):

    def __init__(self):

        self.test_pool = TestPool()

    def _async_run(self, test_name, test_parameters):
        data = list()
        key = self.test_pool.add_test(test_name, TestType.TestBenchmark, test_parameters)
        data.append(key)
        state_ = State.PASS if key is not None else State.ERROR_NOT_FOUND
        result = {"data": data, "state": state_, "msg": "Test {} key {}".format(test_name, key)}
        return result

    def _get_async_result(self, key_):
        results, state = self.test_pool.get_state_by_key(key_)
        data = list()
        data.append(json.dumps(results))
        result = {"msg": "", "state": state, "data":data}
        return result

    @marshal_with(resource_fields, envelope='resource')
    def post(self):
        args = PARSER.parse_args()
        test_parameters = eval(args["parameters"])
        test_name = test_parameters["test_name"]
        result = self._async_run(test_name, test_parameters)
        return result

    @marshal_with(resource_fields, envelope='resource')
    def get(self, key_=None):
        if key_ is not None:
            result = self._get_async_result(key_)
        else:
            result = {"msg": "command did not support", "state": State.ERROR_NOT_FOUND}
        return result
