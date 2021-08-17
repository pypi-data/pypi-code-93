# !/usr/bin/env python3
"""
Python lambda handler code for performing S3 select requests
on Put event.
"""
import logging


def lambda_handler(event, context):
    """Main function for S3 meta data check"""
print("Hello")

if __name__ == "__main__":
    context = {}
    event = {}
    lambda_handler(event, context)

