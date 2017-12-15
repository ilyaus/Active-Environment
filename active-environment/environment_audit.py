import json
import boto3
import environment


AWS_PROFILE = 'tapps'
S3_BUCKET = ''
ENV_STATUS_KEY = ''


def get_json(file_name):
    try:
        with open(file_name, 'r') as fp:
            ret_data = json.load(fp)
    except Exception as ex:
        print(ex)
        ret_data = {}

    return ret_data


def put_json(json_data, file_name):
    try:
        with open(file_name, 'w') as fp:
            fp.write(json.dumps(json_data, indent=2))
    except Exception as ex:
        print(ex)


def run(event, context):
    pass


def main():
    boto3.setup_default_session(profile_name=AWS_PROFILE)
    put_json(environment.audit(get_json('audit-config.json')), 'audit-config-result.json')


if __name__ == "__main__":
    main()
