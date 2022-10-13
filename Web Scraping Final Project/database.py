import boto3
from botocore.exceptions import ClientError
import hashlib, uuid
from boto3.dynamodb.conditions import Key, Attr


########################################################################

#######       METHODS AVAILABLE   #######
#   create_account(company_name)
#   insert_into_<table_name>(company_name, other_fields_in_table)
#   delete_item(company_name, table_name, primary_key, primary_key_value)
#   get_item(company_name, table_name, primary_key, primary_key_value)
#   retrieve_items(company_name, table_name, **kwargs)
########################################################################

AWS_ACCESS_KEY_ID = "*************"
AWS_SECRET_KEY = "***************"

boto_session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_KEY,
                            region_name='us-east-1')

dynamodb = boto_session.resource('dynamodb')
dynamodb_client = boto_session.client('dynamodb')
s3_client = boto_session.client('s3')
#Helper
def get_table_name(company_name, table_name):
    return company_name + '_' + table_name

# Creates a table with given primary key and primary key type
def create_table(name, primary_key, primary_key_type):
    table = dynamodb.create_table(
        TableName=name,
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
            'Value': name
            }
        ]
    )

    #Wait until table is created
    table.meta.client.get_waiter('table_exists').wait(TableName=name)
    print(table.item_count)
    print("Table status:", table.table_status)
    return

#def check_table(name):


# Registers a new account and creates corresponding tables, creates an empty S3 bucket for the company
def create_account(name):
    current_tables = dynamodb_client.list_tables()['TableNames']

    #runs the first time to create an Accounts table
    newname = name + '_users'
    print("Before if 'Accounts' not in current_tables: ")
    if newname not in current_tables:
            # # USERS
        user_table_name = get_table_name(name, 'users')
        create_table(user_table_name, 'username', 'S')


def insert_into_table(table_name, data): # (string, dict) -> None
    table = dynamodb.Table(table_name)
    '''
    test_key = 'test_key1'
    username = 'test_username1'
    password = 'test_password1'
    table.put_item(
        Item={
            'test_key': test_key,
            'username': username,
            'password': password
        }
    )
    '''
    table.put_item(
        Item=data
    )
    print("Successfully inserted data into {} table".format(table_name))
    return

# Returns dictionary of entire row as key value pairs
#response = get_item(company_name, 'users', 'username', username)
def get_item(primary_key_value):
    #table_name = get_table_name(company_name, table_name)
    table_name = primary_key_value + '_users'
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(
            Key={
                'username': primary_key_value
            }
        )
        item = response['Item']
        print('Successfully retrieved item')
        return item
    except ClientError as e:
        print(e.response['Error']['Message'])

    return


### Inserting in all the tables - uses insert_into_table
def insert_into_users(username, password):
    table_name = get_table_name(username, 'users')
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print('Created',password)
    print('Hashed',hashed_password)
    data = {
        'username': username,
        'password': hashed_password,

    }
    insert_into_table(table_name, data)


# Delete item from table
def delete_item(company_name, table_name, primary_key, primary_key_value):
    table_name = get_table_name(company_name, table_name)
    table = dynamodb.Table(table_name)
    try:
        response = table.delete_item(
            Key={
                primary_key: primary_key_value
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
    else:
        print("DeleteItem succeeded:")

def verify_username(username, password):
    response = get_item(username)
    password2 = response['password']
    validate_password = hashlib.sha256(password.encode()).hexdigest()
    print('Hashed entered password: ', validate_password)
    print('Password in DB: ', password2)
    return (1,response['access']) if password2 == validate_password else (0,0)


