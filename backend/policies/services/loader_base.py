from policies.models import Policy
from datetime import date

def update_policy_status(policy):
    today = date.today()

    if policy.start_date and policy.start_date > today:
        policy.status = "upcoming"
    elif policy.end_date and policy.end_date < today:
        policy.status = "expired"
    else:
        policy.status = "active"

    policy.save()


def upsert_policy(source_id, policy_type, fields, raw_json):
    policy, created = Policy.objects.update_or_create(
        source_id=source_id,
        defaults={
            **fields,
            "policy_type": policy_type,
            "raw_json": raw_json,
        }
    )

    update_policy_status(policy)
    return policy
