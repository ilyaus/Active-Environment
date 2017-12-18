import boto3
import json


class AwsDynamoDb:
    _aws_profile = ""
    _aws_region = ""

    _ddb_table_name = ""

    _aws_client = None

    def __init__(self, **kwargs):
        self.properties = kwargs

        self._aws_profile = self.properties.get('aws_profile')
        self._aws_region = self.properties.get('aws_region')
        self._ddb_table_name = self.properties.get('table_name')

        boto3.setup_default_session(profile_name=self._aws_profile)
        self._aws_client = boto3.client('dynamodb', region_name=self._aws_region)

    def save_audit(self, key, json_obj):
        """
        
        :param key: 
        :param json_obj: 
        :return: 
        """

        try:
            response = self._aws_client.get_item(TableName=self._ddb_table_name,
                                                 Key={'AuditDate': {'S': key}})

            if 'Item' in response:
                audit_data = json.loads(response['Item']['AuditData']['S'])
                audit_data.append(json_obj)

                self._aws_client.update_item(TableName=self._ddb_table_name,
                                             Key={'AuditDate': {'S': key}},
                                             UpdateExpression='SET AuditData = :val, AuditCount = :count',
                                             ExpressionAttributeValues={':val': {'S': json.dumps(audit_data)},
                                                                        ':count': {'N': str(len(audit_data))}})
            else:
                audit_data = list()
                audit_data.append(json_obj)
                self._aws_client.put_item(TableName=self._ddb_table_name,
                                          Item={'AuditDate': {'S': key},
                                                'AuditCount': {'N': str(len(audit_data))},
                                                'AuditData': {'S': json.dumps(audit_data)}})

        except Exception as ex:
            print("Error: Failed to save audit ({0})".format(ex))
