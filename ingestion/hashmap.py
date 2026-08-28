import hashlib, hmac, json, os

PII_SALT = os.environ["PII_SALT"]        # .env — jamais dans le script

HASH = {"email"}                         # ← les clés-identité : hashées, pas supprimées

def _hash(value) -> str:
    """Salted HMAC-SHA256, tronqué : déterministe (même email → même hash, les
    jointures et count(distinct) survivent), irréversible sans le sel."""
    normalized = str(value).lower().strip()
    return hmac.new(PII_SALT.encode(), normalized.encode(), hashlib.sha256).hexdigest()[:16]


def scrub_properties(record: dict) -> dict:
    props = record.get("properties")
    if not props:
        return record
    if isinstance(props, str):
        props = json.loads(props)
    for k, v in props.items():
        if k in HASH or (isinstance(v, str) and "@" in v):
            props[k] = _hash(v)          # hashé, jamais supprimé — jointures préservées
    record["properties"] = props
    return record





# def scrub_properties(record: dict) -> dict:
#     """Allowlist sur event.properties : HASH → hashé, KEEP → gardé, le reste DROPPÉ.
#     Tourne pendant l'extraction — la PII n'atteint jamais le lac."""
#     props = record.get("properties")
#     if not props:
#         return record
#     if isinstance(props, str):              # selon le driver, JSON peut arriver en str
#         props = json.loads(props)
#     clean = {}
#     for k, v in props.items():
#         if k in HASH and v:
#             clean[k] = _hash(v)
#         elif k in KEEP:
#             # ceinture-bretelles : une valeur qui RESSEMBLE à un email est hashée quand même
#             clean[k] = _hash(v) if isinstance(v, str) and "@" in v else v
#     record["properties"] = clean
#     return record