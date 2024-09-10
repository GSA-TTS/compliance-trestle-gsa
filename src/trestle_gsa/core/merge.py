import logging
import json

from trestle.common import log

logger = logging.getLogger(f'trestle.{__name__}')
trace = log.Trace(logger)


def deep_merge(a: dict, b: dict) -> dict:
    for key in b:
        trace.log(f'deep_merge key: {key}')
        if key in a and a[key]:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                trace.log(f'Deep merge for {key}')
                deep_merge(a[key], b[key])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                trace.log(f'List merge for {key}')
                a[key] = _deduplicated_list(a[key], b[key])
            else:
                trace.log(f'Not copying key: {key}')
        else:
            trace.log(f'Copying {key} to a')
            a[key] = b[key]
    return a


def _deduplicated_list(a: list, b: list) -> list:
    if len(b) == 0:
        return a
    combined_list = b + a
    if 'id' in a[0] and a[0]['id']:
        # deduplicate by id
        trace.log('Deduplicating by "id"')
        return list({x['id']: x for x in combined_list}.values())
    if 'role_id' in a[0] and a[0]['role_id']:
        # deduplicate by role-id
        trace.log('Deduplicating by "role_id"')
        return list({x['role_id']: x for x in combined_list}.values())
    else:
        try:
            # deduplicate by all fields via json string
            trace.log('Deduplicating by json dump')
            dedupped = set(json.dumps(item, sort_keys=True) for item in combined_list)
            return list(json.loads(x) for x in dedupped)
        except TypeError:
            # error dumping to json, just combine the lists
            trace.log('No deduplication, returning combined_list')
            return combined_list
