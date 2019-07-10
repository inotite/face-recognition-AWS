from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib

print('Loading function')
dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
rekognition.create_collection(CollectionId='BLUEPRINT_COLLECTION')


# --------------- Helper Functions to call Rekognition APIs ------------------



def index_faces(bucket, key):
    print ("Lambda started")
    # Note: Collection has to be created upfront. Use CreateCollection API to create a collecion.
    response = rekognition.index_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}}, CollectionId="BLUEPRINT_COLLECTION")
    return response

def update_index(tableName, faceId, fullName ,athlete_id):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName},
            'athlete_id':{'S' : athlete_id}
        }
    )


# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
       
        # Calls rekognition IndexFaces API to detect faces in S3 object and index faces into specified collection
        response = index_faces(bucket, key)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            ret = s3.head_object(Bucket=bucket, Key=key)
            personFullName = ret['Metadata']['fullname']
            athlete_id = ret['Metadata']['athlete_id']
            update_index('athletes_data', faceId, personFullName ,athlete_id)

        # Print response to console.
        print(response)

        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
