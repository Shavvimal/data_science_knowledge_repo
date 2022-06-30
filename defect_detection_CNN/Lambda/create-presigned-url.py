# Returns a presigned url that can be used to upload xray images directly from the client to an s3 bucket
import logging
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    bucket_name = 'london-innovation-hub'
    object_name = event["filename"]
    fields= None 
    conditions=None
    expiration=3600

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     f'xray/tiff/{object_name}',
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response
    