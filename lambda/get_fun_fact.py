import os
import boto3
from boto3.dynamodb.conditions import Key
import json
from decimal import Decimal

# DynamoDB Resource
dynamodb = boto3.resource('dynamodb')

# S3 Client
s3_client = boto3.client('s3')
bucket_name = 'fun-facts-images'

# Tables
fun_facts_table = dynamodb.Table("FunFact")
landmarks_table = dynamodb.Table("Landmark")


def generate_presigned_url(key):
    return s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=3600)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def handler(event, context):
    # Determine the requested endpoint
    resource = event['resource']

    if resource == '/funFacts':
        landmark_id = event['queryStringParameters']['landmarkId']
        response = fun_facts_table.query(
            KeyConditionExpression=Key('landmarkId').eq(landmark_id)
        )

        items = response['Items']

        # Generate pre-signed URLs for images
        for item in items:
            if 'imageName' in item:
                item['imageUrl'] = generate_presigned_url(f"{item['imageName']}.jpeg")

    elif resource == '/landmarks':
        # Return the first 20 items from the landmarks table
        response = landmarks_table.scan(Limit=20)
        items = response['Items']

        # Generate pre-signed URLs for images
        for item in items:
            if 'image' in item:
                item['imageUrl'] = generate_presigned_url(f"{item['image']}.jpeg")

    else:
        # Handle invalid resource requests
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Invalid resource'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'], default=decimal_default),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
