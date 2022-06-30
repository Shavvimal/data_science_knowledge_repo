import boto3
import botocore
from botocore.exceptions import ClientError
import os
import json

BUCKET_NAME = 'london-innovation-hub'
KEY = f'xray/model_logs.txt'
LOCAL_FILE = '/tmp/accuracy.txt'
s3 = boto3.resource('s3')

def remove_local_file(filePath):
     # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")

def lambda_handler(event, context):
    name = event["name"]
    true_class = event["true_class"]
    model_class = event["model_class"]
    hdwd = event["hdwd"]
    time = event["time"]
    
    try:
        obj=s3.Bucket(BUCKET_NAME).download_file(KEY, LOCAL_FILE)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
            remove_local_file(LOCAL_FILE)
            return {
                'statusCode': 403,
                'body': json.dumps(f'Unsuccessful in adding name:{name}, time:{time}, true_class:{true_class}, model_class:{model_class} & hdwd:{hdwd} to {KEY}')
                
            }

        else:
            raise
    with open('/tmp/accuracy.txt', 'a') as fd:
        fd.write(f"{name}	{time}	{true_class}	{model_class}	{hdwd}\n")

    s3.meta.client.upload_file(LOCAL_FILE, BUCKET_NAME, KEY)
    
    return {
    'statusCode': 200,
    'body': json.dumps(f'Succesfully added name:{name}, time:{time}, true_class:{true_class}, model_class:{model_class} & hdwd:{hdwd} to {KEY}')
        
    }
    
    
#     import boto3
# import botocore
# from botocore.exceptions import ClientError
# import os
# import json

# BUCKET_NAME = 'london-innovation-hub'
# KEY = f'xray/accuracy.txt'
# LOCAL_FILE = '/tmp/accuracy.txt'
# s3 = boto3.resource('s3')

# def remove_local_file(filePath):
#      # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
#     if os.path.exists(filePath):
#         os.remove(filePath)
#     else:
#         print("Can not delete the file as it doesn't exists")

# def lambda_handler(event, context):
#     append_text = event["append_text"]
#     try:
#         obj=s3.Bucket(BUCKET_NAME).download_file(KEY, LOCAL_FILE)
#     except ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             print("The object does not exist.")
#             remove_local_file(LOCAL_FILE)
#             return {
#                 'statusCode': 403,
#                 'body': json.dumps(f'Unsuccessful in adding {append_text} to {KEY}')
                
#             }

#         else:
#             raise
#     with open('/tmp/accuracy.txt', 'a') as fd:
#         fd.write(f"{append_text}\n")

#     s3.meta.client.upload_file(LOCAL_FILE, BUCKET_NAME, KEY)
    
#     return {
#     'statusCode': 200,
#     'body': json.dumps(f'Succesfully added \'{append_text}\' to {KEY}')
        
#     }