import socket
from datetime import datetime
import xli_utilities as utils


def audit(config, timestamp='now'):
    """
    config is predefined JSON object which must contain the following objects:
    - audit        : defines how audit is performed
    - environments : defines environments
    
    :param config: 
    :param timestamp
    :return: 
    """

    if timestamp == 'now':
        timestamp = datetime.utcnow().isoformat()

    active_env = find_active(config)

    config['environments'] = update_environments(config['environments'], active_env, timestamp)

    return config


def minify(environment):
    """
    environment is predefined JSON object.  Each object must contain at least these keys:
    - name              : used to identify environment
    - active            : indicates if environment is currently active
    - became-active     : ISO timestamp when environment became active
    - last-time-active  : ISO timestamp when environment was active last (last audit time)
    - region            : Active region name
    
    this function returns object with just those keys (all other keys are removed)

    :param environment: 
    :return: 
    """
    ret_val = {}

    try:
        ret_val['name'] = environment['name']
        ret_val['active'] = environment['active']
        ret_val['became-active'] = environment['became-active']
        ret_val['last-time-active'] = environment['last-time-active']
        ret_val['region'] = environment['region']
    except KeyError as ex:
        print("ERROR: required key is not present ({0})".format(ex))
    except Exception as ex:
        print("Error: {0}".format(ex))

    return ret_val


def set_all_inactive(environments):
    for e in environments:
        e['active'] = False

    return environments


def get_current_active_environment(environments):
    active_count = 0
    ret_val = {}

    for e in environments:
        if e['active']:
            ret_val = e
            active_count += 1

    if active_count > 1:
        raise RuntimeError("Found more than one active environments")

    return ret_val


def update_last_active(environments, timestamp):
    """

    :param environments: 
    :param timestamp: 
    :return: 
    """
    ret_val = environments

    for e in ret_val:
        if e['active']:
            e['last-time-active'] = timestamp

    return ret_val


def update_became_active(environments, env_name, timestamp):
    ret_val = set_all_inactive(environments)

    for e in ret_val:
        if e['name'] == env_name:
            e['last-time-active'] = timestamp
            e['became-active'] = timestamp
            e['active'] = True

    return ret_val


def update_environments(environments, active_env, timestamp):
    """
    environments is predefined JSON list.  Each object must contain at least these keys:
    - name              : used to identify environment
    - active            : indicates if environment is currently active
    - became-active     : ISO timestamp when environment became active
    - last-time-active  : ISO timestamp when environment was active last (last audit time)
    - region            : Active region name

    Only one environment in the list can be active
        
    :param environments: 
    :param active_env: 
    :param timestamp:
    :return: 
    """

    current_active_env = get_current_active_environment(environments)

    if 'name' in current_active_env and current_active_env['name'] == active_env:
        ret_val = update_last_active(environments, timestamp)
    else:
        ret_val = update_became_active(environments, active_env, timestamp)

    return ret_val


def find_active(config):
    return find_active_by_type(config['audit'])


def find_active_by_type(audit_config):
    if audit_config['type'] == 'url':
        return find_active_by_url(audit_config['params'])


def find_active_by_url(params):
    host_info = socket.gethostbyname_ex(params['url'])

    return utils.do_match(params['regex'], host_info[0], params['match_group'])
