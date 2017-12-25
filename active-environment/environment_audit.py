import os
import environment
import s3
import dynamo_db


AWS_PROFILE = ''
AWS_REGION = ''
S3_BUCKET = ''
ENV_STATUS_KEY = 'audit-config.json'
ENV_STATUS_KEY_RESULT = 'audit-config-result.json'
DB_TABLE_NAME = ''


def get_global_var(var):
    if var == 'AWS_PROFILE': return AWS_PROFILE
    elif var == 'AWS_REGION': return AWS_REGION
    elif var == 'S3_BUCKET': return S3_BUCKET
    elif var == 'ENV_STATUS_KEY': return ENV_STATUS_KEY
    elif var == 'ENV_STATUS_KEY_RESULT': return ENV_STATUS_KEY_RESULT
    elif var == 'DB_TABLE_NAME': return DB_TABLE_NAME


def set_var(var):
    return os.environ[var] if var in os.environ else get_global_var(var)


def get_variables():
    local_vars = {
        'AWS_PROFILE': '',
        'AWS_REGION': '',
        'S3_BUCKET': '',
        'ENV_STATUS_KEY': '',
        'ENV_STATUS_KEY_RESULT': '',
        'DB_TABLE_NAME': ''
    }

    for var in local_vars:
        local_vars[var] = set_var(var)

    return local_vars


def run(event, context):
    local_vars = get_variables()

    s3_obj = s3.AwsS3(s3=local_vars['S3_BUCKET'])
    ddb_obj = dynamo_db.AwsDynamoDb(table_name=local_vars['DB_TABLE_NAME'])

    audit_data = environment.audit(s3_obj.get_json(local_vars['ENV_STATUS_KEY']))
    active_environment = environment.minify(environment.get_current_active_environment(audit_data['environments']))

    s3_obj.put_json(ENV_STATUS_KEY_RESULT, audit_data)
    ddb_obj.save_audit(active_environment['last-time-active'].split('T')[0], active_environment)


def main():
    pass


if __name__ == "__main__":
    main()
