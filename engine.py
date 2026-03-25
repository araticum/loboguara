import re
from typing import Dict, Any, List, Optional
from .models import Rule

_REGEX_SUFFIX = "_regex"


def evaluate_rules(
    event_payload: Dict[str, Any], active_rules: List[Rule]
) -> Optional[Rule]:
    """
    Avalia os campos de entrada do evento contra as regras ativas cadastradas no banco.
    Uma regra tem `condition_json` (ex: {"source": "prometheus", "severity": "CRITICAL"}).

    Suporta dois tipos de match:
    - campo exato: {"source": "oasis-radar"}
    - regex: {"service_regex": ".*celery.*"} → testa re.fullmatch contra o campo "service"

    Retorna a primeira regra que bater com as condições (AND simples).
    """
    for rule in active_rules:
        condition = rule.condition_json
        is_match = True
        for key, value in condition.items():
            if key.endswith(_REGEX_SUFFIX):
                field_name = key[: -len(_REGEX_SUFFIX)]
                field_value = event_payload.get(field_name, "")
                if not re.fullmatch(value, str(field_value), re.IGNORECASE):
                    is_match = False
                    break
            else:
                if event_payload.get(key) != value:
                    is_match = False
                    break

        if is_match:
            return rule

    return None
