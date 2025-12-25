from datetime import date

from policies.models import Policy


def update_policy_status(policy):
    today = date.today()

    if policy.start_date and policy.start_date > today:
        policy.status = "UPCOMING"
    elif policy.end_date and policy.end_date < today:
        policy.status = "EXPIRED"
    else:
        policy.status = "ACTIVE"

    policy.save(update_fields=["status"])


def upsert_policy(source_id, policy_type, fields, raw):
    policy, _ = Policy.objects.update_or_create(
        source_id=source_id,
        defaults={
            **fields,
            "policy_type": policy_type,
            "raw": raw,
        },
    )

    update_policy_status(policy)
    return policy
