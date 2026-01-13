"""
Credential Vault: Secure storage and retrieval of API keys and secrets
Never logs secrets; integrates with OS keyring in production
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CredentialVault:
    """Secure credential storage with encryption"""
    
    def __init__(self, vault_path: Optional[Path] = None, use_os_keyring: bool = False):
        self.use_os_keyring = use_os_keyring
        if vault_path is None:
            vault_path = Path(__file__).parent.parent.parent / "config" / "credentials.json.encrypted"
        self.vault_path = vault_path
        self._cipher = None
        self._load_or_create_cipher()
    
    def _load_or_create_cipher(self):
        """Load or create encryption cipher"""
        # For MVP: use a simple key derivation from env var or default
        # In production, use OS keyring
        key_material = os.getenv("EARNETICS_VAULT_KEY", "default_dev_key_change_in_production")
        
        if self.use_os_keyring:
            try:
                import keyring
                key_material = keyring.get_password("earnetics", "vault_key") or key_material
            except ImportError:
                pass  # Fallback to env var
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'earnetics_vault_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
        self._cipher = Fernet(key)
    
    def get_secret(self, key_id: str) -> Optional[str]:
        """
        Get secret by key_id
        
        NEVER logs the secret value
        """
        try:
            if not self.vault_path.exists():
                # Try environment variable first
                env_key = os.getenv(key_id.upper().replace("-", "_"))
                if env_key:
                    return env_key
                return None
            
            # Load encrypted vault
            with open(self.vault_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self._cipher.decrypt(encrypted_data)
            vault = json.loads(decrypted_data.decode())
            
            # Get secret
            if key_id in vault:
                return vault[key_id]
            
            # Fallback to environment variable
            env_key = os.getenv(key_id.upper().replace("-", "_"))
            if env_key:
                return env_key
            
            return None
        except Exception as e:
            print(f"Error retrieving secret {key_id}: {e}")
            # Fallback to environment variable
            env_key = os.getenv(key_id.upper().replace("-", "_"))
            if env_key:
                return env_key
            return None
    
    def store_secret(self, key_id: str, secret: str) -> bool:
        """Store secret (encrypted)"""
        try:
            # Load existing vault or create new
            vault = {}
            if self.vault_path.exists():
                with open(self.vault_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self._cipher.decrypt(encrypted_data)
                vault = json.loads(decrypted_data.decode())
            
            # Add/update secret
            vault[key_id] = secret
            
            # Encrypt and save
            vault_json = json.dumps(vault)
            encrypted_data = self._cipher.encrypt(vault_json.encode())
            
            self.vault_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.vault_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error storing secret {key_id}: {e}")
            return False
    
    def list_keys(self) -> list:
        """List all stored key IDs (without values)"""
        try:
            if not self.vault_path.exists():
                return []
            
            with open(self.vault_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._cipher.decrypt(encrypted_data)
            vault = json.loads(decrypted_data.decode())
            
            return list(vault.keys())
        except Exception as e:
            print(f"Error listing keys: {e}")
            return []
