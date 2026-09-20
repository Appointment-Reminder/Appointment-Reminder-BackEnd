import re
from typing import Any

FIELD_KEY_PATTERN = re.compile(r"^q(?P<qid>\d+)_[^\[]*(?:\[(?P<subkey>[^\]]*)\])?$")

def parse_jotform_raw_request( raw_request: dict[str, Any] ) -> dict[str, dict]:
    """
        Converts Jotform's webhook rawRequest (keyed like "q3_name", "q3_name[first]",
        "q28_addons[]", "q100_typeA100") into {qid: {"answer": value}} — the shape
        resolve_submission expects.
        """
    result: dict[str, dict] = {}
    for key, value in raw_request.items():
        match = FIELD_KEY_PATTERN.match(key)
        if not match:
            continue  # not a question field — skip Jotform metadata keys like "submitDate", "buildDate", etc.

        qid = match.group("qid")
        subkey = match.group("subkey")

        if subkey is None:
            # plain field: "q100_typeA100": "A - 30 MINUTES..."
            result[qid] = {"answer": value}

        elif subkey == "":
            # checkbox/array field: "q28_addons[]" — value is already a list from Jotform
            result[qid] = {"answer": value if isinstance(value, list) else [value]}

        else:
            # composite field: "q3_name[first]", "q3_name[last]" — merge into one dict per qid
            entry = result.setdefault(qid, {"answer": {}})
            if not isinstance(entry["answer"], dict):
                entry["answer"] = {}
            entry["answer"][subkey] = value

    return result