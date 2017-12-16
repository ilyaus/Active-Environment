import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import environment
import xli_utilities as utils
import s3


class MyTestCase(unittest.TestCase):
    AWS_PROFILE = 'tapps'
    AWS_REGION = 'us-east-1'
    S3_BUCKET = 'st-halo-audit'
    ENV_STATUS_KEY = 'audit-config.json'
    ENV_STATUS_KEY_RESULT = 'audit-config-result.json'

    # @unittest.skip
    def test_environment_audit_s3(self):
        s3_obj = s3.AwsS3(aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION, s3=self.S3_BUCKET)
        s3_obj.put_json(self.ENV_STATUS_KEY_RESULT, environment.audit(s3_obj.get_json(self.ENV_STATUS_KEY)))

    # @unittest.skip
    def test_environment_audit_local(self):
        utils.put_json(self.ENV_STATUS_KEY_RESULT, environment.audit(utils.get_json(self.ENV_STATUS_KEY)))


if __name__ == '__main__':
    unittest.main()
