#  Takes the clients decision of defect or non-defect and moves the .jpeg image to the respective classified folder for use in continuous learning.
import json
import os
import io
import boto3

def lambda_handler(event, context):
    filename = event["filename"]
    classification = event["classification"]
    
    bucket = 'london-innovation-hub'
    new_file_key = f'xray/{classification}/{filename}'
    old_file_key = f'xray/unclassified_jpeg/{filename}'
    
    s3 = boto3.resource('s3')
    # copy image from unclassified folder to the new folder either classified_defect or classified_non_defect
    s3.Object(bucket, new_file_key).copy_from(CopySource=f'{bucket}/{old_file_key}')
    # delete the image from the unclassified folder
    s3.Object(bucket, old_file_key).delete()
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Image successfully moved from {old_file_key} to {new_file_key}')
    }
