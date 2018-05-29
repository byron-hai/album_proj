#coding: utf-8

import boto3

BODY_HTML = """
<html>
<head></head>
<body>
    <h1> Service Notification</h1>
    <p>Ignore please. For testing</p>
</body>
</html>
"""
ses = boto3.client('ses')
def lambda_handler(event, context):
    '''
    event = {'from': '', 'to': '', 'subject': '', 'message': ''}
    '''
    if not ('from' in event or 'to' in event or 'subject' in event or 'message' in event):
        return {'code': 1, 'message': 'Not all value(s) provided'}

    email_from = event['from']
    email_to = event['to']
    subject = event['subject']
    message = event['message']

    client = boto3.client('ses')
    response = ses.send_email(
        Source = email_from,
        Destination={
            'ToAddresses': [email_to],
            },
            
        Message={
            'Subject': {
                'Data': subject,
                },
            'Body': {
                'Text': {
                    'Data': message,
                }
            }
        },
    )

    return {'code': 0, 'message': 'success'}

event={'from':'', 'to': '', 'subject': 'Test', 'message': 'This is a useless message'}
lambda_handler(event, '')
