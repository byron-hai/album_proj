#coding: utf-8

import boto3
import logging
from flask import current_app as app
from boto3.dynamodb.conditions import Key, Attr

FMT = '%(levelname)-6s %(message)s'
logging.basicConfig(level='INFO', format=FMT)

class DynamoDB:
    def __init__(self, region=None, logging=logging, debug=False):
        self.region = region
        self.logger = logging.getLogger(self.__class__.__name__)

        self.conn = boto3.resource('dynamodb', region_name=self.region)
        if self.conn and debug:
            self.logger.debug('DB connected')

    def insert_item(self, table_name, item_dict):
        ''' Insert an item to table '''
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item_dict)

        return True if \
        response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

    def delete_item(self, table_name, item):
        ''' delete an item from table '''
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.delete_item(item)
        return True if \
        response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

    def update_item(self, table_name, item):
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        try:
            response = table.update_item(item)
            return True if \
            response['ResponseMetadata']['HTTPStatusCode'] == 200 else False
        except Exception as err:
            self.logger.error(str(err))
            return False

    def query_item(self, table_name, key, value):
        ''' query a item from table '''
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        try:
            response = table.query(
                KeyConditionExpression=Key(key).eq(value))
            items = response['Items']
            return items
        except Exception as err:
            self.logger.error(str(err))
            return
 
    def scan_item(self, table_name, key, value):
        ''' scan table to get all items '''
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        try:
            response = table.scan(
                FilterExpression=Attr(key).eq(value))
            items = response['Items']
            return items
        except Exception as err:
            self.logger.error(str(err))
            return

    def get_item(self, table_name, query_item):
        ''' Get an Item from its key '''
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=query_item)
        item = response['Item']
        return item

    def create_table(self, table_name=None, attr_dict=None, throughput='1'):
        ''' Create table by attr_dict '''
        if self._isTable_exists(table_name):
            self.logger.info('Table: %s already exists', table_name)
            return

        if not isinstance(attr_dict, dict):
            self.logger.error("attr_dict must be an dict")
            return

        dict_len = len(attr_dict)
        if dict_len == 1: 
            dynamodb = self.conn
            table = dynamodb.create_table(
                KeySchema=[
                    {
                        'AttributeName': attr_dict['hash_name'],
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                       'AttributeName': attr_dict['hash_name'],
                       'AttributeType': 'S'
                    },
                ],
                ProvisionedThroughput={
                   'ReadCapacityUnits': int(throughput),
                   'WriteCapacityUnits': int(throughput)
                },
            TableName=table_name,
            )

            if table:
                self.logger.info('Table created')
            return table

        elif dict_len == 2:
            dynamodb = self.conn
            table = dynamodb.create_table(
                KeySchema=[
                    {
                        'AttributeName': attr_dict['hash_name'],
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': attr_dict['range_name'],
                        'KeyType': 'RANGE'
                    },
                ],
                AttributeDefinitions=[
                    {
                       'AttributeName': attr_dict['hash_name'],
                       'AttributeType': 'S'
                    },
                    {
                       'AttributeName': attr_dict['range_name'],
                       'AttributeType': 'S'
                    },
                ],
                ProvisionedThroughput={
                   'ReadCapacityUnits': int(throughput),
                   'WriteCapacityUnits': int(throughput)
                },

            TableName=table_name)

            if table:
                self.logger.info('Table created')
            return table
        else:
             self.logger.error("Not an valid attr_dict")
             return
 
    def _isTable_exists(self, table_name):
        dynamodb = self.conn
        try:
           table = dynamodb.Table(table_name)
           is_exists = table.table_status in ("CREATING", "UPDATING", "DELETING", "ACTIVE")
           return is_exists
        except Exception as err:
            self.logger.error(str(err))
            return

    def delete_table(self, table_name):
        dynamodb = self.conn
        try:
            table = dynamodb.Table(table_name)
            table.delete()
            self.logger.info('Table: %s, deletion finished', table_name)
            return True

        except Exception as err:
            self.logger.error("Table: %s does not exist. %s", table_name, str(err))
            return False

