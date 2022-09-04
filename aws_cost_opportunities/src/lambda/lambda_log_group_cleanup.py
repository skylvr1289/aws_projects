import os
import json
import boto3

def delete_redundant_lambda_logs(region: str):
    lambda_client = boto3.client('lambda', region_name = region)
    lambda_paginator = lambda_client.get_paginator('list_functions')
    existing_functions = set()
    page_count =0
    count = 0
    for response in lambda_paginator.paginate():
        print('page: %s'%str(page_count))
        page_count = page_count+1
        for function in response['Functions']:
            count = count+1
            existing_functions.add(function['FunctionName'])

    print('Total valid existing functions: %s'%str(count))
    # list all lambda log groups
    cw_client = boto3.client('logs', region_name = region)
    paginator = cw_client.get_paginator('describe_log_groups')
    count = 0
    deleted_logs = []
    for page in paginator.paginate(logGroupNamePrefix = '/aws/lambda/'):
        print('log page: '+ str(count))
        count = count +1
        for group in page['logGroups']:
            #'/aws/lambda/function_name'
            log_lambda_name = group['logGroupName'].split('/')[3]
            if(log_lambda_name not in existing_functions):
                print('deleting log group: %s' %{group['logGroupName']})
                cw_client.delete_log_group(logGroupName = group['logGroupName'])
                deleted_logs.append(group['logGroupName'])
    print('deleted %s lambda log groups'%{len(deleted_logs)})

if __name__== '__main__':
    regions = json.loads(os.environ.get('REGIONS', '["us-west-2", "us-east-1"]'))
    for region in regions:
        delete_redundant_lambda_logs('us-west-2')