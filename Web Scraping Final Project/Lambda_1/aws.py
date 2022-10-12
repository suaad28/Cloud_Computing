from ast import Attribute
import base64
from pyclbr import Function
import boto3
from botocore.exceptions import ClientError
import json
import hashlib

class aws_config():
    AWS_ACCESS_KEY_ID = "*********************"
    AWS_SECRET_ACCESS_KEY = "*******************"
    REGION_NAME = "us-east-1"


class s3_client():
    def __init__(self):
        self.client = boto3.client('s3',
            aws_access_key_id = aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = aws_config.AWS_SECRET_ACCESS_KEY,
            region_name = aws_config.REGION_NAME)
        self.bucketName = "ece1779-bucket-a3"

    def upload(self, fname, key):
        self.client.put_object(Body=fname, Bucket=self.bucketName, Key = key)
        print("Successfully upload!")

    def fetch_file(self, key):
        try:
            res = self.s3_client.get_object(Bucket = self.bucketName, Key = key)
            print("Successfully fetched!")
            f_content = base64.b64encode(res['Body'].read()).decode()
            return f_content
        except ClientError as e:
            print("Error", e)
            return e

class dynamodb():
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id = aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = aws_config.AWS_SECRET_ACCESS_KEY,
            region_name = aws_config.REGION_NAME)
        self.dynamodb = self.session.resource('dynamodb')
        self.client = self.session.client('dynamodb')

    def create_table(self, tname, primary_key, primary_key_type):
        table = self.dynamodb.create_table(
            TableName=tname,
            KeySchema=[
                {
                    'AttributeName': primary_key,
                    'KeyType': 'HASH'  #Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': primary_key,
                    'AttributeType': primary_key_type
                },     
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            Tags=[
                {
                'Key': 'TableName',
                'Value': tname
                }
            ]
        )

        table.meta.client.get_waiter('table_exists').wait(TableName=tname)
        print("Table created!")
        return 
    
    def get_info(self, table_name, primary_key, key_value):
        table = self.dynamodb.Table(table_name)
        try:
            response = table.get_item(
                Key={
                    primary_key: key_value
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            item = response['Item']
            print('Successfully retrieved item')
            return item
        return None

    def insert_into_table(self, tname, data): # (string, dict) -> None
        table = self.dynamodb.Table(tname)
        print("data is: ", data)
        table.put_item(
            Item=data
        )
        print("Successfully inserted data into {} table".format(tname))
        return

    def verify_username(self, uname, pw):
        table = self.dynamodb.Table('account_info')
        response = table.get_item(
                Key={
                    'username': uname
                }
            )
        if 'Item' not in response:
            print('Invalid company name')
            return(0,0)
        print(response['Item'])
        #print('Entered password: ', pw)
        response = self.get_info('account_info', 'username', uname)
        db_hpw = response['password']
        hpw = hashlib.sha256(pw.encode()).hexdigest()
        print('Hashed entered password: ', hpw)
        print('Password in DB: ', db_hpw)
        return 1 if db_hpw == hpw else 0

    def create_account(self, uname, pw):
        l_table = self.client.list_tables()['TableNames']
        #runs the first time to create an Accounts table
        if 'account_info' not in l_table:
            self.create_table('account_info', 'username', 'S')

        hpw = hashlib.sha256(pw.encode()).hexdigest()
        new_account = {'username': uname, 'password': hpw}
        print("New Account is: ", new_account)
        self.insert_into_table('account_info', new_account)

class lambda_client():
    def __init__(self):
        self.client = boto3.client('lambda',
            aws_access_key_id = aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = aws_config.AWS_SECRET_ACCESS_KEY,
            region_name = aws_config.REGION_NAME)

    def invoke(self, fname, data):
        json_data = json.dumps(data, default=str)
        return self.client.invoke(FunctionName = fname, Payload = json_data)
