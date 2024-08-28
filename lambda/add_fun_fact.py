import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('User')


def handler(event, context):
    body = json.loads(event['body'])
    user_id = body.get('userId')

    # Check if the user exists
    response = users_table.get_item(Key={'userId': user_id})
    user_exists = 'Item' in response

    if user_exists:
        # Update user metadata
        update_expression = "set username = :u, email = :e, profilePicture = :p, userCategory = :c, updatedAt = :a"
        expression_attribute_values = {
            ':u': body['username'],
            ':e': body['email'],
            ':p': body.get('profilePicture', None),
            ':c': body.get('userCategory', 'Rookie'),
            ':a': datetime.now().isoformat()
        }

        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        message = 'User metadata updated successfully'
    else:
        # Create new user metadata
        user_metadata = {
            'userId': user_id,
            'username': body['username'],
            'email': body['email'],
            'createdAt': datetime.now().isoformat(),
            'profilePicture': body.get('profilePicture', None),
            'userCategory': body.get('userCategory', 'Rookie'),
        }

        users_table.put_item(Item=user_metadata)
        message = 'User metadata added successfully'

    return {
        'statusCode': 201,
        'body': json.dumps({'message': message, 'userId': user_id}),
        'headers': {
            'Content-Type': 'application/json'
        }
    }