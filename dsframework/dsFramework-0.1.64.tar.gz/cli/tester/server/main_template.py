from typing import Union, List

import logging

if __name__ == "main":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)  # TODO read from config

from pythonjsonlogger import jsonlogger

logger = logging.getLogger()

formatter = jsonlogger.JsonFormatter()

for handler in logger.handlers:
    handler.setFormatter(formatter)

import os
import json
import uvicorn
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from pipeline.pipeline import generatedProjectNamePipeline
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs
from server.test_scheme.test_input import TestInputRequest
from server.test_scheme.test_output import TestOutputResponse

async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token": # todo: please replace with realistic token
        raise HTTPException(status_code=400, detail="X-Token header invalid")

def load_allowed_cors_origins():
    allowed_origins = []
    cors_origin_list_path = 'server/cors_allowed_origins.json'
    if os.path.exists(cors_origin_list_path):
        with open(cors_origin_list_path) as f:
            allowed_origins = json.load(f)

    return allowed_origins


app = FastAPI()

origins = load_allowed_cors_origins()
methods = ["*"]
headers = ["*"]
credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=credentials,
    allow_methods=methods,
    allow_headers=headers,
)

pipeline = generatedProjectNamePipeline()
# from server.pool import InstancePool
# pipelines = [generatedProjectNamePipeline() for i in range(3)]
# app.pipelines = InstancePool(pipelines)

@app.post('/predict', dependencies=[Depends(get_token_header)])
def predict(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    '''
    predict api
    '''
    data = body.dict()
    logger.info({"message": "predict invoked", "data": json.dumps(data)})
    print('data', data)

    # call model here
    try:
        output: List[generatedProjectNameOutputs] = pipeline.execute(**data)
    except Exception as ex:
        logger.exception(msg=data, exc_info=True)
        output = {'error': {'request': ex}}
    # call model here
    return output

@app.post('/parse', dependencies=[Depends(get_token_header)])
def parse(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    '''
    parse api
    '''
    data = body.dict()
    logger.info({"message": "parse invoked", "data": json.dumps(data)})
    print('data', data)

    # call model here
    try:
        output: List[generatedProjectNameOutputs] = pipeline.execute(**data)
    except Exception as ex:
        logger.exception(msg=data, exc_info=True)
        output = {'error': {'request': data}}
    # call model here
    return output

@app.post('/test', dependencies=[Depends(get_token_header)])
def test(body: TestInputRequest) -> List[TestOutputResponse]:
    '''
    test api
    '''
    body = body.dict()
    logger.info({"message": "test invoked", "test": json.dumps(body)})
    print('body', body)

    # call tester here
    response = []
    rows = body['rows']
    truth_dataset_id = body['truth_dataset_id']
    model_type_id = body['model_type_id']
    for row in rows:
        data = json.loads(row['data'])
        id = row['id']
        raw_id = row['raw_id'] or -1
        segments = data['segments'] if 'segments' in data else data
        pred = data['segments'] if 'segments' in data else data
        text = ''
        if 'signature' in data:
            text = data['signature']
        elif 'email' in data:
            text = data['email']
        elif 'text' in data:
            text = data['text']
        elif 'name' in data:
            text = data['name']
        response.append(
            TestOutputResponse(
                **{
                    'truth_id': id,
                    'truth_dataset_id': truth_dataset_id,
                    'model_type_id': model_type_id,
                    'raw_id': raw_id,
                    'pred': json.dumps(pred),
                    'target': json.dumps(segments),
                    'text': text,
                    'name_first_fn': 0,
                    'name_first_fp': 0,
                    'name_first_pred': "Marty",
                    'name_first_prob': -1,
                    'name_first_target': "Marty",
                    'name_first_tn': 0,
                    'name_first_tp': 1,
                }
            )
        )
    # call tester here

    return response

@app.get("/livenessprobe")
def liveness_probe():
    return {"alive": True}


@app.get("/readinessprobe")
def readiness_probe():
    return {"ready": True}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

