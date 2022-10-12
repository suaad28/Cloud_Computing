import boto3
from datetime import datetime
from app import webapp, cw_client



# No need for this https request
# keep it here for original logic
# def record_requests():
#     # Put custom metrics
#     cw_client.put_metric_data(
#         MetricData=[
#             {
#                 'MetricName': 'HTTP_request',
#                 'Dimensions': [
#                     {
#                         'Name': 'INSTANCE_ID',
#                         'Value': webapp.config['INSTANCE_ID']
#                     },
#                 ],
#                 'Timestamp': datetime.utcnow(),
#                 'Unit': 'Count',
#                 'Value': 1.0
#             },
#         ],
#         Namespace='SITE/TRAFFIC'
#     )


'''
Call the record function in routers.py while each time we have a miss
'''
def record_miss():
    # Put custom metrics
    cw_client.put_metric_data(
        MetricData=[
            {
                'MetricName': 'MISS',
                'Dimensions': [
                    {
                        'Name': 'INSTANCE_ID',
                        'Value': webapp.config['INSTANCE_ID']
                    },
                ],
                'Timestamp': datetime.utcnow(),
                'Unit': 'Count',
                'Value': 1.0
            },
        ],
        Namespace='SITE/TRAFFIC'
    )


'''
Call the record function in routers.py while each time we have a success hit
'''
def record_hit():
    # Put custom metrics
    cw_client.put_metric_data(
        MetricData=[
            {
                'MetricName': 'HIT',
                'Dimensions': [
                    {
                        'Name': 'INSTANCE_ID',
                        'Value': webapp.config['INSTANCE_ID']
                    },
                ],
                'Timestamp': datetime.utcnow(),
                'Unit': 'Count',
                'Value': 1.0
            },
        ],
        Namespace='SITE/TRAFFIC'
    )