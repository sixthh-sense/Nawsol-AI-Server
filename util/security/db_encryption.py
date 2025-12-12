"""
데이터베이스 암호화/복호화 유틸리티

Fernet (AES-128-CBC + HMAC) 기반 대칭키 암호화 사용
- 타임스탬프 기반 암호문 (재생 공격 방지)
- 무결성 검증 (HMAC)
- URL-safe Base64 인코딩
"""

from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from config.encryption_config import EncryptionConfig
from util.log.log import Log

logger = Log.get_logger()


class DBEncryption:
    """
    데이터베이스 필드 암호화/복호화 유틸리티
    
    특징:
    - Singleton 패턴으로 Fernet 인스턴스 재사용
    - 자동 에러 처리 및 로깅
    - 빈 값 처리 최적화
    """
    
    _fernet: Optional[Fernet] = None
    
    @classmethod
    def _get_fernet(cls) -> Fernet:
        """
        Fernet 인스턴스 가져오기 (Singleton)
        
        Returns:
            Fernet: 암호화 인스턴스
        """
        if cls._fernet is None:
            try:
                key = EncryptionConfig.get_encryption_key()
                cls._fernet = Fernet(key)
                logger.info("🔐 암호화 시스템 초기화 완료")
            except Exception as e:
                logger.error(f"❌ 암호화 시스템 초기화 실패: {e}")
                raise
        return cls._fernet
    
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """
        문자열 암호화
        
        Args:
            plaintext: 평문 문자열
        
        Returns:
            str: Base64 인코딩된 암호문 (URL-safe)
        
        Examples:
            >>> encrypted = DBEncryption.encrypt("john@example.com")
            >>> print(encrypted)
            'gAAAAABmK...'
        """
        if not plaintext:
            return ""
        
        try:
            fernet = cls._get_fernet()
            encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
            encrypted_str = encrypted_bytes.decode('utf-8')
            
            logger.debug(f"🔒 암호화 완료 (길이: {len(plaintext)} → {len(encrypted_str)})")
            return encrypted_str
        
        except Exception as e:
            logger.error(f"❌ 암호화 실패: {e}")
            raise ValueError(f"암호화 중 오류 발생: {e}")
    
    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """
        문자열 복호화
        
        Args:
            ciphertext: Base64 인코딩된 암호문
        
        Returns:
            str: 복호화된 평문
        
        Examples:
            >>> decrypted = DBEncryption.decrypt("gAAAAABmK...")
            >>> print(decrypted)
            'john@example.com'
        """
        if not ciphertext:
            return ""
        
        try:
            fernet = cls._get_fernet()
            decrypted_bytes = fernet.decrypt(ciphertext.encode('utf-8'))
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            logger.debug(f"🔓 복호화 완료 (길이: {len(ciphertext)} → {len(decrypted_str)})")
            return decrypted_str
        
        except InvalidToken:
            logger.error("❌ 복호화 실패: 잘못된 토큰 또는 변조된 데이터")
            raise ValueError("복호화 실패: 암호화 키가 변경되었거나 데이터가 손상되었습니다")
        
        except Exception as e:
            logger.error(f"❌ 복호화 실패: {e}")
            raise ValueError(f"복호화 중 오류 발생: {e}")
    
    @classmethod
    def encrypt_int(cls, value: int) -> str:
        """
        정수 암호화 (금액 등)
        
        Args:
            value: 정수값
        
        Returns:
            str: 암호화된 문자열
        
        Examples:
            >>> encrypted = DBEncryption.encrypt_int(3000000)
            >>> print(encrypted)
            'gAAAAABmK...'
        """
        if value is None:
            return ""
        
        return cls.encrypt(str(value))
    
    @classmethod
    def decrypt_int(cls, ciphertext: str) -> int:
        """
        정수 복호화
        
        Args:
            ciphertext: 암호화된 문자열
        
        Returns:
            int: 복호화된 정수값
        
        Examples:
            >>> decrypted = DBEncryption.decrypt_int("gAAAAABmK...")
            >>> print(decrypted)
            3000000
        """
        if not ciphertext:
            return 0
        
        try:
            plaintext = cls.decrypt(ciphertext)
            return int(plaintext)
        except ValueError as e:
            logger.error(f"❌ 정수 변환 실패: {e}")
            return 0
    
    @classmethod
    def encrypt_float(cls, value: float) -> str:
        """
        실수 암호화
        
        Args:
            value: 실수값
        
        Returns:
            str: 암호화된 문자열
        """
        if value is None:
            return ""
        
        return cls.encrypt(str(value))
    
    @classmethod
    def decrypt_float(cls, ciphertext: str) -> float:
        """
        실수 복호화
        
        Args:
            ciphertext: 암호화된 문자열
        
        Returns:
            float: 복호화된 실수값
        """
        if not ciphertext:
            return 0.0
        
        try:
            plaintext = cls.decrypt(ciphertext)
            return float(plaintext)
        except ValueError as e:
            logger.error(f"❌ 실수 변환 실패: {e}")
            return 0.0
