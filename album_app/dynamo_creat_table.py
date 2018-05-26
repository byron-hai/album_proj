# -*- coding: utf-8 -*-

import boto3

dynamodb = boto3.resource('dynamodb')

img_tbl = dynamodb.create_table(
    TableName='photos',
    KeySchema=[
        {
            'AttributeName': 'UserId',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'ImageId',
            'KeyType': 'RANGE'
        },
        {
            'AttributeName': 'ImageUrl',
            'KeyType': 'RANGE'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'UserId',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'ImageId',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'ImageUrl',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughout={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    },
)

print("Table status", img_tbl.table_status)
