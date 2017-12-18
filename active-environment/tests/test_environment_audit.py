import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import environment
import xli_utilities as utils
import s3
import dynamo_db


class MyTestCase(unittest.TestCase):
    AWS_PROFILE = 'tapps'
    AWS_REGION = 'us-east-1'
    S3_BUCKET = 'st-halo-audit'
    ENV_STATUS_KEY = 'test-audit-config.json'
    ENV_STATUS_KEY_RESULT = 'test-audit-config-result.json'
    DB_TABLE_NAME = 'st-EnvironmentAudit'

    # @unittest.skip
    def test_environment_audit_s3(self):
        s3_obj = s3.AwsS3(s3=self.S3_BUCKET, aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION)
        s3_obj.put_json(self.ENV_STATUS_KEY_RESULT, environment.audit(s3_obj.get_json(self.ENV_STATUS_KEY)))

    # @unittest.skip
    def test_environment_audit_local(self):
        utils.put_json(self.ENV_STATUS_KEY_RESULT, environment.audit(utils.get_json(self.ENV_STATUS_KEY)))

    def test_environment_audit_dynamo(self):
        s3_obj = s3.AwsS3(s3=self.S3_BUCKET, aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION)
        ddb_obj = dynamo_db.AwsDynamoDb(table_name=self.DB_TABLE_NAME, aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION)

        audit_data = environment.audit(s3_obj.get_json(self.ENV_STATUS_KEY))
        active_environment = environment.minify(environment.get_current_active_environment(audit_data['environments']))
        ddb_obj.save_audit(active_environment['last-time-active'].split('T')[0], active_environment)

if __name__ == '__main__':
    unittest.main()
