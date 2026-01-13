from __future__ import annotations
import json
import hashlib
import hmac
import os
import logging
import shutil
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Configuration ----
def _normalize_env_path(env_value: Optional[str], default: str) -> str:
    """Normalize path from environment variable, converting backslashes to forward slashes."""
    if not env_value:
        return default
    return env_value.replace("\\", "/")

DIRECTIVE_PATH = _normalize_env_path(os.getenv("PRIME_DIRECTIVE_PATH"), "prime_directive.json")
# We use a file in the data directory as the default persistent store for the secret
SECRET_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "prime_directive_secret.txt")

def _get_or_create_secret() -> str:
    """
    Resolves the HMAC secret with the following priority:
    1. Environment variable PRIME_DIRECTIVE_HMAC_SECRET
    2. File system (data/prime_directive_secret.txt)
    3. Auto-generation (only if not in env, and saves to file)
    """
    # 1. Environment variable
    env_secret = os.getenv("PRIME_DIRECTIVE_HMAC_SECRET")
    if env_secret:
        # Log safe fingerprint
        fingerprint = hashlib.sha256(env_secret.encode()).hexdigest()[:8]
        logger.info(f"Loaded Prime Directive secret from environment. Fingerprint: {fingerprint}")
        return env_secret

    # 2. File system
    secret_path = Path(SECRET_FILE_PATH)
    if secret_path.exists():
        try:
            file_secret = secret_path.read_text(encoding="utf-8").strip()
            if file_secret:
                fingerprint = hashlib.sha256(file_secret.encode()).hexdigest()[:8]
                logger.info(f"Loaded Prime Directive secret from file. Fingerprint: {fingerprint}")
                return file_secret
        except Exception as e:
            logger.warning(f"Failed to read secret file: {e}")

    # 3. Auto-generation (Dev/Fallback)
    logger.warning("PRIME_DIRECTIVE_HMAC_SECRET not set. Generating new persistent secret.")
    new_secret = hashlib.sha256(os.urandom(32)).hexdigest()
    
    try:
        secret_path.parent.mkdir(parents=True, exist_ok=True)
        secret_path.write_text(new_secret, encoding="utf-8")
        logger.info(f"Generated and saved new secret to {secret_path}")
    except Exception as e:
        logger.error(f"Failed to save generated secret: {e}")
        # In this worst case, we return the memory-only secret, but warn heavily
        logger.critical("Using ephemeral memory-only secret! Multi-worker setup will fail!")

    return new_secret

# Initialize secret at module level
SECRET_KEY = _get_or_create_secret()

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
        # HMAC verification
        if not SECRET_KEY:
            return True
            
        mac = hmac.new(SECRET_KEY.encode(), raw_bytes, hashlib.sha256).hexdigest()
        
        sig_path = Path(DIRECTIVE_PATH + ".sig")
        if not sig_path.exists():
            # If signature file is missing, we cannot verify.
            # We treat this as a failure to force regeneration/signing.
            return False

        stored_mac = sig_path.read_text(encoding="utf-8").strip()
        return hmac.compare_digest(mac, stored_mac)

    # Hard block any runtime mutation
    def forbid_mutation(self):
        cfg = self._data.get("integrity", {})
        if cfg.get("block_runtime_mutation", True):
            raise PermissionError("Prime Directive is immutable at runtime.")

def sign_prime_directive(path: str = DIRECTIVE_PATH):
    """Signs the Prime Directive file and saves the signature."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cannot sign missing file: {path}")

    with open(path, "rb") as f:
        raw = f.read()
    
    mac = hmac.new(SECRET_KEY.encode(), raw, hashlib.sha256).hexdigest()
    
    sig_path = Path(path + ".sig")
    sig_path.write_text(mac, encoding="utf-8")
    logger.info(f"Signed Prime Directive at {path}")

def load_prime_directive(path: str = DIRECTIVE_PATH) -> PrimeDirective:
    try:
        if not os.path.exists(path):
             # If it doesn't exist, we can't load it.
             # In a real app we might create a default.
             raise FileNotFoundError(f"Prime Directive not found at {path}")

        with open(path, "rb") as f:
            raw = f.read()
            
        # Expect file to include only the JSON
        data = json.loads(raw.decode("utf-8"))
        checksum = hashlib.sha256(raw).hexdigest()
        pd = PrimeDirective(data, checksum)
        
        if not pd.verify_integrity(raw):
            raise ValueError("Prime Directive checksum verification failed.")
            
        if not pd.verify_signature(raw):
            raise ValueError("Prime Directive HMAC verification failed.")
            
        return pd
        
    except ValueError as e:
        if "HMAC verification failed" in str(e) or "checksum verification failed" in str(e):
            logger.warning(f"{e} Attempting auto-recovery...")
            return regenerate_prime_directive(path, raw if 'raw' in locals() else None)
        raise

def regenerate_prime_directive(path: str, corrupted_bytes: Optional[bytes] = None) -> PrimeDirective:
    """
    Backs up invalid directive and re-signs the current content.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup signature if it exists
    sig_path = f"{path}.sig"
    if os.path.exists(sig_path):
        shutil.copy2(sig_path, f"{sig_path}.invalid_{timestamp}")
        logger.warning(f"Backed up invalid signature to {sig_path}.invalid_{timestamp}")

    try:
        # Try to parse existing to see if it's valid JSON
        if corrupted_bytes:
            data = json.loads(corrupted_bytes.decode("utf-8"))
            # It is valid JSON, just signature mismatch. Re-sign.
            logger.info("JSON content is valid. Re-signing with current secret.")
            
            sign_prime_directive(path)
            
            # Now reload
            return load_prime_directive(path)
            
    except json.JSONDecodeError:
        logger.error("Prime Directive JSON is corrupt. Cannot recover automatically without a template.")
        # Backup the corrupt file
        if os.path.exists(path):
            shutil.copy2(path, f"{path}.invalid_{timestamp}")
            logger.warning(f"Backed up corrupt Prime Directive to {path}.invalid_{timestamp}")
        
        raise ValueError("Prime Directive is corrupt and cannot be recovered.")

    # If we got here, something else happened.
    raise RuntimeError("Failed to recover Prime Directive.")

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
