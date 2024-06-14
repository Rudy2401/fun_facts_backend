import os
import boto3
import json
from datetime import datetime
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
fun_facts_table = dynamodb.Table(os.environ['FUN_FACTS_TABLE_NAME'])


def handler(event, context):
    body = json.loads(event['body'])
    fun_fact = {
        'landmarkId': body['landmarkId'],
        'funFactId': str(uuid4()),
        'submittedBy': body['submittedBy'],
        'createdAt': datetime.utcnow().isoformat(),
        'description': body['description'],
        'likes': 0,
        'dislikes': 0,
        'approvalStatus': 'pending',
        'approvedBy': None,
        'rejectedBy': None,
        'image': body['image'],
        'tags': body['tags'],
        'source': body['source']
    }

    fun_facts_table.put_item(Item=fun_fact)

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Fun fact added successfully'}),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
