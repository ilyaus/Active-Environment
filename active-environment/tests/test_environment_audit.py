import unittest
import sys
import os
import copy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import environment
import xli_utilities as utils
import s3
import dynamo_db


class ActiveEnvironmentTestCase(unittest.TestCase):
    AWS_PROFILE = 'tapps'
    AWS_REGION = 'us-east-1'
    S3_BUCKET = 'st-halo-audit'
    DB_TABLE_NAME = 'st-EnvironmentAudit'

    base_environment = {
        'name': 'TestEnv',
        'active': False,
        'became-active': '',
        'last-time-active': '',
        'region': ''
    }

    base_environments = [
        {
            'name': 'TestEnv-a',
            'active': False,
            'became-active': '',
            'last-time-active': '',
            'region': ''
        },
        {
            'name': 'TestEnv-b',
            'active': True,
            'became-active': '',
            'last-time-active': '',
            'region': ''
        },
        {
            'name': 'TestEnv-c',
            'active': False,
            'became-active': '',
            'last-time-active': '',
            'region': ''
        }
    ]

    # ---- End to End tests
    # currently there is no validation for those (will add it later)
    # @unittest.skip
    def test_environment_audit_s3_set_active(self):
        env_status_key = 'test-audit-config.json'
        env_status_key_result = 'test-audit-config-result.json'
        expected_result = 'test-audit-config-expected-result.json'
        timestamp = '2000-01-01T01:00:00.00000'

        s3_obj = s3.AwsS3(s3=self.S3_BUCKET, aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION)
        s3_obj.copy_to_s3(env_status_key)

        s3_obj.put_json(env_status_key_result, environment.audit(s3_obj.get_json(env_status_key), timestamp=timestamp))

        self.assertEqual(utils.get_json(expected_result), s3_obj.get_json(env_status_key_result),
                         "Audit result is not correct")

    # @unittest.skip
    def test_environment_audit_s3_update_active(self):
        env_status_key = 'test-audit-config-update.json'
        env_status_key_result = 'test-audit-config-update-result.json'
        expected_result = 'test-audit-config-update-expected-result.json'
        timestamp = '2000-01-02T01:00:00.00000'

        s3_obj = s3.AwsS3(s3=self.S3_BUCKET, aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION)
        s3_obj.copy_to_s3(env_status_key)

        s3_obj.put_json(env_status_key_result, environment.audit(s3_obj.get_json(env_status_key), timestamp=timestamp))

        self.assertEqual(utils.get_json(expected_result), s3_obj.get_json(env_status_key_result),
                         "Audit result is not correct")

    # @unittest.skip
    def test_environment_audit_local_set_active(self):
        env_status_key = 'test-audit-config.json'
        env_status_key_result = 'test-audit-config-result.json'
        expected_result = 'test-audit-config-expected-result.json'
        timestamp = '2000-01-01T01:00:00.00000'

        utils.put_json(env_status_key_result, environment.audit(utils.get_json(env_status_key), timestamp=timestamp))

        self.assertEqual(utils.get_json(expected_result), utils.get_json(env_status_key_result),
                         "Audit result is not correct")

    # @unittest.skip
    def test_environment_audit_local_update_active(self):
        env_status_key = 'test-audit-config-update.json'
        env_status_key_result = 'test-audit-config-update-result.json'
        expected_result = 'test-audit-config-update-expected-result.json'
        timestamp = '2000-01-02T01:00:00.00000'

        utils.put_json(env_status_key_result, environment.audit(utils.get_json(env_status_key), timestamp=timestamp))

        self.assertEqual(utils.get_json(expected_result), utils.get_json(env_status_key_result),
                         "Audit result is not correct")

    @unittest.skip
    def test_environment_audit_dynamo(self):
        env_status_key = 'test-audit-config.json'

        s3_obj = s3.AwsS3(s3=self.S3_BUCKET, aws_profile=self.AWS_PROFILE, aws_region=self.AWS_REGION)
        ddb_obj = dynamo_db.AwsDynamoDb(table_name=self.DB_TABLE_NAME,
                                        aws_profile=self.AWS_PROFILE,
                                        aws_region=self.AWS_REGION)

        audit_data = environment.audit(s3_obj.get_json(env_status_key))
        active_environment = environment.minify(environment.get_current_active_environment(audit_data['environments']))
        ddb_obj.save_audit(active_environment['last-time-active'].split('T')[0], active_environment)

    # ---- Environment function tests
    # @unittest.skip
    def test_minify(self):
        test_env = copy.deepcopy(self.base_environment)
        test_env['key-a'] = 'test-key-a'
        test_env['key-b'] = 'test-key-b'

        result = environment.minify(test_env)

        self.assertEqual(result, self.base_environment, "Minify did not produce correct result")

    # @unittest.skip
    def test_set_all_inactive(self):
        test_envs = copy.deepcopy(self.base_environments)

        result = environment.set_all_inactive(test_envs)

        for env in result:
            self.assertFalse(env['active'], "Environment 'active' property is not set correctly")

    # @unittest.skip
    def test_get_current_active_environment(self):
        test_envs = copy.deepcopy(self.base_environments)

        result = environment.get_current_active_environment(test_envs)

        self.assertEqual(result['name'], 'TestEnv-b', "Did not find correct active environment")

    # @unittest.skip
    def test_update_last_active(self):
        test_envs = copy.deepcopy(self.base_environments)
        timestamp = '2000-01-01T01:00:00.00000'
        found_active = False

        result = environment.update_last_active(test_envs, timestamp)

        for env in result:
            if env['active']:
                self.assertEqual(env['last-time-active'], timestamp,
                                 "Did not find correct last-time-active timestamp")
                self.assertEqual(env['name'], 'TestEnv-b')
                found_active = True
            else:
                self.assertEqual(env['last-time-active'], '',
                                 "Did not find correct last-time-active timestamp")

        self.assertTrue(found_active, "Did not find active environment")

    # @unittest.skip
    def test_update_became_active(self):
        test_envs = copy.deepcopy(self.base_environments)
        timestamp = '2000-01-01T01:00:00.00000'
        new_active_name = 'TestEnv-c'
        found_active = False

        result = environment.set_all_inactive(test_envs)
        result = environment.update_became_active(result, new_active_name, timestamp)

        for env in result:
            if env['active']:
                self.assertEqual(env['became-active'], timestamp,
                                 "Did not find correct became-active timestamp")

                self.assertEqual(env['last-time-active'], timestamp,
                                 "Did not find correct last-time-active timestamp")
                self.assertEqual(env['name'], new_active_name, "Environment name is not correct")
                found_active = True
            else:
                self.assertEqual(env['last-time-active'], '',
                                 "Did not find correct last-time-active timestamp")

        self.assertTrue(found_active, "Did not find active environment")

    # @unittest.skip
    def test_update_environments(self):
        test_envs = copy.deepcopy(self.base_environments)
        timestamp = '2000-01-01T01:00:00.00000'
        new_active_name = 'TestEnv-c'
        found_active = False

        result = environment.update_environments(test_envs, new_active_name, timestamp)

        for env in result:
            if env['active']:
                self.assertEqual(env['became-active'], timestamp,
                                 "Did not find correct became-active timestamp")

                self.assertEqual(env['last-time-active'], timestamp,
                                 "Did not find correct last-time-active timestamp")
                self.assertEqual(env['name'], new_active_name, "Environment name is not correct")
                found_active = True
            else:
                self.assertEqual(env['last-time-active'], '',
                                 "Did not find correct last-time-active timestamp")

        self.assertTrue(found_active, "Did not find active environment")


if __name__ == '__main__':
    unittest.main()
