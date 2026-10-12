"""Keep domain and address alternatives independent for routing and DNS."""
DOMAIN_KEYS = ('domain_suffix', 'domain', 'domain_keyword', 'domain_regex')
MATCH_KEYS = DOMAIN_KEYS + ('ip_cidr',)


def split_rule(rule):
    """Split an unrestricted domain/IP OR rule into equivalent sibling rules."""
    if set(rule) - set(MATCH_KEYS):
        raise ValueError('Only unrestricted domain/IP rules may be split')
    domains = {key: rule[key] for key in DOMAIN_KEYS if rule.get(key)}
    addresses = {'ip_cidr': rule['ip_cidr']} if rule.get('ip_cidr') else {}
    return [part for part in (domains, addresses) if part]


def unrestricted(payload):
    """Aggregate old mixed and new separate rules for coverage and deltas."""
    result = {key: set() for key in MATCH_KEYS}
    for rule in payload['rules']:
        if set(rule) - set(MATCH_KEYS):
            continue
        for key in MATCH_KEYS:
            result[key].update(rule.get(key, []))
    return {key: sorted(values) for key, values in result.items()}


def scoped_rules(payload):
    return [rule for rule in payload['rules'] if set(rule) - set(MATCH_KEYS)]
