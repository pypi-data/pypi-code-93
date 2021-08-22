import logging
from typing import Optional, Dict

import websockets.exceptions
from classiq import client
from classiq_interface.analyzer import result as analysis_result, analysis_params
from classiq_interface.combinatorial_optimization import optimization_problem
from classiq_interface.combinatorial_optimization.result import OptimizationResult
from classiq_interface.execute import execute_problem, result as execute_result
from classiq_interface.generator import constraints, result as generator_result
from classiq_interface.hybrid import vqe_problem, result as hybrid_result
from classiq_interface.server import routes


class ApiWrapper:
    def __init__(self):
        self._client = client.client()

    async def _call_task(self, http_method: str, url: str, body: Optional[Dict] = None):
        try:
            res = await self._client.call_api(
                http_method=http_method, url=url, body=body
            )
        except client.ExpiredTokenError:
            self._client.update_expired_access_token()
            res = await self._client.call_api(
                http_method=http_method, url=url, body=body
            )

        return res

    async def _generation_task(
        self, constraints_obj: constraints.QuantumCircuitConstraints
    ) -> generator_result.GenerationResult:
        async with self._client.establish_websocket_connection(
            path="/api/v1/ws/generate"
        ) as websocket:
            await websocket.send(constraints_obj.json())

            while await (msg := websocket.recv()):
                logging.info(msg)

            res = await websocket.recv()
            return generator_result.GenerationResult.parse_raw(res)

    async def call_generation_task(
        self, constraints_obj: constraints.QuantumCircuitConstraints
    ) -> generator_result.GenerationResult:
        try:
            return await self._generation_task(constraints_obj=constraints_obj)
        except websockets.exceptions.InvalidStatusCode:
            # Note: currently, the server returns status code 500, although one could expect 401. This is due to
            # FastAPI limitation - https://github.com/encode/starlette/pull/527
            # Note: This is probably not the proper place to retry,  but as I am using a context manager, I could not
            #       find an easy alternative.
            self._client.update_expired_access_token()
            return await self._generation_task(constraints_obj=constraints_obj)

    async def call_execute_task(
        self, problem: execute_problem.ExecuteProblem
    ) -> execute_result.ExecutionResult:
        data = await self._call_task(
            http_method="post",
            url=routes.EXECUTE_FULL_PATH,
            body=problem.dict(),
        )

        if not isinstance(data, dict):
            raise Exception(f"Unexpected returned value: {data}")

        return execute_result.ExecutionResult.parse_obj(data)

    async def call_analysis_task(
        self, params: analysis_params.AnalysisParams
    ) -> analysis_result.AnalysisResult:
        data = await self._call_task(
            http_method="post",
            url=routes.ANALYZER_FULL_PATH,
            body=params.dict(),
        )

        if not isinstance(data, dict):
            raise Exception(f"Unexpected returned value: {data}")

        return analysis_result.AnalysisResult.parse_obj(data)

    async def call_hybrid_task(
        self, problem: vqe_problem.VQEProblem
    ) -> hybrid_result.HybridResult:
        data = await self._call_task(
            http_method="post",
            url=routes.HYBRID_FULL_PATH,
            body=problem.dict(),
        )

        if not isinstance(data, dict):
            raise Exception(f"Unexpected returned value: {data}")

        return hybrid_result.HybridResult.parse_obj(data)

    async def call_combinatorial_optimization_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> OptimizationResult:
        data = await self._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_FULL_PATH,
            body=problem.dict(),
        )

        if not isinstance(data, dict):
            raise Exception(f"Unexpected returned value: {data}")

        return OptimizationResult.parse_obj(data)
