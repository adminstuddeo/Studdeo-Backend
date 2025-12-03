from pwdlib import PasswordHash

hassher: PasswordHash = PasswordHash.recommended()


class SecurityService:
    def hash_password(self, password: str) -> str:
        return hassher.hash(password=password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return hassher.verify(password=plain_password, hash=hashed_password)
