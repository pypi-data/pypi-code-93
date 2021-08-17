# !/usr/bin/env python3
"""
Python lambda handler code for performing S3 select requests
on Put event.
"""
import logging
import os
import boto3
import datetime


def lambda_handler(event, context):    
    print("Hello")


if __name__ == "__main__":
    event = {}
    context = {}
    lambda_handler(event, context)
