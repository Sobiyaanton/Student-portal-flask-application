import boto3
import key_config as keys

dynamodb_client = boto3.client(
    'dynamodb',
    aws_access_key_id=keys.ACCESS_KEY_ID,
    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
    region_name=keys.REGION_NAME,
)
dynamodb_resource = boto3.resource(
    'dynamodb',
    aws_access_key_id=keys.ACCESS_KEY_ID,
    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
    region_name=keys.REGION_NAME,
)

def create_table():
    table = dynamodb_resource.create_table(
        TableName='students',
        KeySchema=[
            {
                'AttributeName': 'registration_number',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'email',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'registration_number',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

