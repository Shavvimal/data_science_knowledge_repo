#  Converts the .tif xray image to a .jpeg and passes this image to the sagemaker model endpoint to create a defect prediction.

import os
import io
import boto3
import json
 
import base64 
import numpy as np
import PIL.Image
from PIL import Image

# grab environment variables
ENDPOINT_NAME = 'xray-defect-endpoint'
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    # ## !!! new code below !!!
    
    # grab the tiff file from s3 bucket 
    s3 = boto3.client('s3')
    filename = event['filename']
    key=f'xray/tiff/{filename}'
    bucket = 'london-innovation-hub'
    response = s3.get_object(Bucket=bucket, Key=key)
    file_stream = response['Body']
    im = Image.open(file_stream)
    # convert to a jpeg
    converted_image = im.convert("RGB")
    
    in_mem_file = io.BytesIO()
    converted_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)
    new_file_name = filename.split(".tif")[0] + ".jpeg"
    # Save as unclassified jpeg
    
    upload_key = f'xray/unclassified_jpeg/{new_file_name}'
    s3.upload_fileobj(
        in_mem_file,
        bucket,
        upload_key,
    )
    
    # delete tiff file
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, key).delete()
    
    
    # send jpeg to sagemaker endpoint
    try:
        payload = np.array([np.asarray(converted_image.resize((1024, 1024)))])
        payload = json.dumps(payload.tolist())
        response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                      ContentType='application/json',
                                      Body=payload)
        result = json.loads(response['Body'].read().decode())
        return result
        
    except:
        return {"Error": "Unable to invoke endpoint"}
    
    # # !!! end of new code !!!
    
    
    
    # !!! old code below !!!
    # data = json.loads(json.dumps(event))
    # image_64_encode = data['data']
    # image_64_decode = base64.decodestring(image_64_encode.encode()) 
    
    # with open('/tmp/decodedimage.jpeg', 'wb') as fout:
    #  fout.write(image_64_decode)
    #     # The image is saved this way so in the future we can direct it towards the corect s3
    
    # payload_image = PIL.Image.open('/tmp/decodedimage.jpeg')
    
    # payload = np.array([np.asarray(payload_image.resize((1024, 1024)))])
    # # payload = np.asarray(payload).astype(float).tolist()
    
    # payload = json.dumps(payload.tolist())
    
    # response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
    #                                   ContentType='application/json',
    #                                   Body=payload)

    # print(response)
    # result = json.loads(response['Body'].read().decode())
    # print(result)
    # return result
    # !!! end of old code !!!