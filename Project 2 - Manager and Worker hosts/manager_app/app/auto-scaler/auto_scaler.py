'''
This implement auto-scaler as describled in part2:

- The auto-scaler should be implemented as a stand-alone program that runs in the background.
- Monitoring the miss rate of the mecache pool by getting this information using the AWS CloudWatch API.
- Automatically resizes the memcache pool based on configuration values set by the manager-app.
'''

import sys
import os

#####TODO#####
# All paths here should be changed to ours
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('../../')
sys.path.append(dir_path)
sys.path.append('/home/ubuntu/Desktop/ece1779_lab/A2/manager_app/')


import time
from datetime import datetime, timedelta
from config import Config
from app.aws import AwsClient
import csv
import logging


#####TODO#####
# No need for this cpu util
# keep it here for original logic
# def cpu_utils_avg(aws_client):
#     target_instances = aws_client.get_target_instances()
#     instance_ids = []
#     cpu_sum = 0.0
#     cpu_avg = 0.0
#     point_counter = 0
#     for instance in target_instances:
#         #####TODO##### 
#         # Average for all nodes in the pool over the past 1 minute
#         start_time = datetime.utcnow() - timedelta(seconds = 60)
#         end_time = datetime.utcnow()
#         period = 60
#         cpu_data = aws_client.get_cpu_utilization(instance['id'], start_time, end_time, period)
#         for point in cpu_data:
#             point_counter += 1
#             cpu_sum += point[1]
#     if int(point_counter) >= 1:
#         cpu_avg = cpu_sum / float(point_counter)
#         return cpu_avg
#     return -1

'''
This funciton tries to calculate the total miss rate over all workers
'''
def calc_overall_miss_rate(aws_client):
    target_instances = aws_client.get_target_instances()
    instance_ids = []
    miss_cnt = 0
    hit_cnt = 0
    for instance in target_instances:
        # set start time to 1 minute ago
        start_time = datetime.utcnow() - timedelta(seconds = 60)
        end_time = datetime.utcnow()
        period = 60
        # get the mertic info for miss counts
        # this should return a list of number(counts)
        miss_rate_data = aws_client.get_miss_counts(instance['id'], start_time, end_time, period)
        hit_rate_data = aws_client.get_hit_counts(instance['id'], start_time, end_time, period)
        
        #accumulate all miss counts
        for mc in miss_rate_data:
            miss_cnt += mc[1]

        #accumulate all hit counts
        for hc in hit_rate_data:
            hit_cnt += hc[1]

    # validate all counts are legal
    if int(miss_cnt) >= 0 and int(hit_cnt) >= 0:
        return int(miss_cnt) / (int(miss_cnt) + int(hit_cnt))

    # return -1 means error happened
    return -1


'''
This funciton tries to toggle the worker pool size on AWS side
'''
def auto_scaling(aws_client):
    top_folder = Config.TOP_FOLDER
    policy_file_path = top_folder + '/app/auto-scaler/auto_scale.txt'
    
    #####TODO##### 
    # Limit the maximum size of the worker pool set by auto-scaler to 8 and the minimum to 1
    pool_size_lower_bound = 1
    pool_size_upper_bound = 8

    # declare configures & init to 0s
    # i. Max Miss Rate threshold ( average for all nodes in the pool over the past 1 minute) for growing the pool
    miss_rate_grow_threshold = 0.0
    # ii. Min Miss Rate threshold ( average for all nodes in the pool over the past 1 minute) for shrinking the pool
    miss_rate_shrink_threshold = 0.0  
    # iii. Ratio by which to expand the pool (e.g., expand the ratio of 2.0 doubles the number of memcache nodes).
    grow_ratio = 0.0
    # iv. Ratio by which to shrink the pool (e.g., shrink ratio of 0.5 shuts down 50% of the current memcache nodes).
    shrink_ratio = 0.0
    # auto_scale is the boolean to enable auto-scaler
    auto_scale = 0

    # read policy file and setup configures
    if os.path.exists(policy_file_path):        
        with open(policy_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for row in reader:
                miss_rate_grow_threshold = float(row[0])
                miss_rate_shrink_threshold = float(row[1])
                grow_ratio = float(row[2])
                shrink_ratio = float(row[3])
                auto_scale = int(row[4])
    else:
        logging.error('No policy file found')
        return None

    # start auto-scaler
    if int(auto_scale) == 1:

        # get the list of current instances
        target_instances = aws_client.get_target_instances()
        pool_size = len(target_instances)

        # get the overall miss rate 
        miss_rate = calc_overall_miss_rate(aws_client = aws_client)

        # no valid instances
        logging.info('Overall miss rate is {}'.format(miss_rate))
        logging.info('Current worker pool size is {}'.format(pool_size))
        
        # return error: no workers
        if miss_rate == -1:
            logging.error('No valid workers in the pool')
            return None
        
        # the average in past one minute higher than threshold: growing the pool size
        elif miss_rate > miss_rate_grow_threshold:
            # calc number of pool to grow
            num_to_grow = int(pool_size * (grow_ratio - 1))
            # if current pool full already (8):return no change
            if int(pool_size) >= pool_size_upper_bound:
                logging.warning('Pool size already exceeds the limit')
                return None
            # if just touch the upperbound(8): return success & warn
            elif int(pool_size + num_to_grow) >= pool_size_upper_bound:
                logging.warning('Grow to the limit')
                response = aws_client.grow_worker_by_some(int(pool_size_upper_bound - pool_size))
                logging.warning('Status are {}'.format(response))
                return 'Success'
            # if within upper bound: return success
            else:
                logging.warning('Grow {} instances'.format(num_to_grow))
                response = aws_client.grow_worker_by_some(num_to_grow)
                logging.warning('Status are {}'.format(response))
                return 'Success'
        
        # the average in past one minute lower than threshold: shrinking the pool size
        elif miss_rate < miss_rate_shrink_threshold:
            # calc number of pool to shrink
            num_to_shrink = int(pool_size) - int(pool_size / shrink_ratio)
            # if current pool size is min (1): return no change
            if int(pool_size) <= pool_size_lower_bound:
                logging.warning('Pool size cannot be smaller')
                return None
            # if just touch the lowerbound(1): return success & warn
            elif int(pool_size - num_to_shrink) <= pool_size_lower_bound:
                logging.warning('Shrink to the limit')
                response = aws_client.shrink_worker_by_some(int(pool_size - pool_size_lower_bound))
                logging.warning('Status are {}'.format(response))
                return 'Success'
            # if above lowerbound: return success    
            else:
                logging.warning('Shrink {} instances'.format(num_to_shrink))
                response = aws_client.shrink_worker_by_some(num_to_shrink)
                logging.warning('Status are {}'.format(response))
                return 'Success'

        # the average is between lowerbound & upperbound: return no change
        else:
            logging.warning('Nothing changes')
            return None
    # if no auto-scaler is enabled: return no change
    else:
        logging.error('Auto Scaling is not enabled')
        return None
            

if __name__ == '__main__':
    # initialize an aws client
    aws_client = AwsClient(
        access_key_id = Config.ACCESS_KEY_ID, 
        secrete_key = Config.SECRET_KEY, 
        region = Config.REGION, 
        template_id = Config.TEMPLATE_ID, 
        target_arn = Config.TARGET_ARN,
        elb_dns = Config.ELB_DNS)
    
    # trigger auto-scaling
    logging.getLogger().setLevel(logging.INFO)
    while True:
        response = auto_scaling(aws_client)
        if response == 'Success':
            logging.info('Grow or shrink successfully')
        else:
            logging.info('Auto scale nothing')
        time.sleep(60)
