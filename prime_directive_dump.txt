from __future__ import annotations
import json, hashlib, hmac, os
from typing import Any, Dict

# ---- Configuration ----
DIRECTIVE_PATH = os.getenv("PRIME_DIRECTIVE_PATH", "prime_directive.json")
# Set this in your .env / secret store. Do NOT hardcode in repo.
SECRET_KEY = os.getenv("PRIME_DIRECTIVE_SECRET")

class PrimeDirective:
    def __init__(self, data: Dict[str, Any], checksum: str):
        self._data = data
        self._checksum = checksum

    @property
    def data(self) -> Dict[str, Any]:
        # Expose read-only dict (shallow); enforce mutation via helpers if ever allowed.
        return json.loads(json.dumps(self._data))

    def verify_integrity(self, raw_bytes: bytes) -> bool:
        cfg = self._data.get("integrity", {})
        if not cfg.get("enforce_checksum", True):
            return True
        algo = cfg.get("checksum_algorithm", "SHA256").lower()
        if algo != "sha256":
            raise ValueError("Unsupported checksum algorithm")
        computed = hashlib.sha256(raw_bytes).hexdigest()
        return computed == self._checksum

    def verify_signature(self, raw_bytes: bytes) -> bool:
        # Optional HMAC (recommended). Provide SECRET_KEY in environment.
        if not SECRET_KEY:
            return True
        mac = hmac.new(SECRET_KEY.encode(), raw_bytes, hashlib.sha256).hexdigest()
        # Store/compare this MAC wherever you keep your golden value (e.g., env, vault, or separate file).
        golden_mac = os.getenv("PRIME_DIRECTIVE_MAC")
        return (golden_mac is None) or (mac == golden_mac)

    # Hard block any runtime mutation
    def forbid_mutation(self):
        cfg = self._data.get("integrity", {})
        if cfg.get("block_runtime_mutation", True):
            raise PermissionError("Prime Directive is immutable at runtime.")

def load_prime_directive(path: str = DIRECTIVE_PATH) -> PrimeDirective:
    with open(path, "rb") as f:
        raw = f.read()
    # Expect file to include only the JSON—checksum computed over raw bytes.
    data = json.loads(raw.decode("utf-8"))
    checksum = hashlib.sha256(raw).hexdigest()
    pd = PrimeDirective(data, checksum)
    if not pd.verify_integrity(raw):
        raise ValueError("Prime Directive checksum verification failed.")
    if not pd.verify_signature(raw):
        raise ValueError("Prime Directive HMAC verification failed.")
    return pd

# Threat handling helpers (call from your security layer)
def classify_risk(action: str) -> str:
    # TODO: wire in your own classifier / policy map.
    high = {"alter_legal_entity", "delete_ledger", "push_prod_with_unvetted_model"}
    moderate = {"rotate_keys", "reprice_all", "pause_pipeline"}
    if action in high:
        return "RED"
    if action in moderate:
        return "YELLOW"
    return "GREEN"

def require_authorization(risk: str) -> bool:
    if risk == "GREEN":
        return True
    if risk == "YELLOW":
        # enforce justification + rollback plan upstream
        return True
    if risk == "RED":
        # enforce cryptographic owner approval (DeepAgent UI step, signed token, etc.)
        return False
    return False
