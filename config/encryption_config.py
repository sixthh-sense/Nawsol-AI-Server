"""
데이터베이스 암호화 설정

보안 요구사항:
1. ENCRYPTION_KEY는 절대 코드 저장소에 커밋 금지
2. .env 파일은 .gitignore에 추가
3. GitHub Actions Secrets에 ENCRYPTION_KEY 등록
4. 프로덕션에서는 환경 변수로 주입

생성된 암호화 키:
ENCRYPTION_KEY=qAAVyccKRCMbt3QrJxsA7IE5QNvuyjpg6fTIIRCjRYM=
"""

import os
from functools import lru_cache
from cryptography.fernet import Fernet


class EncryptionConfig:
    """암호화 키 관리 설정"""
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_encryption_key() -> bytes:
        """
        암호화 키 로드
        
        우선순위:
        1. 환경 변수 ENCRYPTION_KEY
        2. .env 파일 (python-dotenv로 자동 로드)
        
        Returns:
            bytes: 암호화 키
            
        Raises:
            ValueError: 키를 찾을 수 없는 경우
        """
        key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY not found! "
                "환경 변수 또는 .env 파일에 설정해주세요.\n"
                "예시: ENCRYPTION_KEY=qAAVyccKRCMbt3QrJxsA7IE5QNvuyjpg6fTIIRCjRYM="
            )
        
        # 키 유효성 검증
        try:
            Fernet(key.encode())
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {e}")
        
        return key.encode()
    
    @staticmethod
    def generate_new_key() -> str:
        """
        새로운 암호화 키 생성 (최초 설정 시에만 사용)
        
        사용법:
        >>> from config.encryption_config import EncryptionConfig
        >>> new_key = EncryptionConfig.generate_new_key()
        >>> print(f"ENCRYPTION_KEY={new_key}")
        
        Returns:
            str: Base64 인코딩된 새 암호화 키
        """
        return Fernet.generate_key().decode()
    
    @staticmethod
    def is_key_configured() -> bool:
        """
        암호화 키가 설정되어 있는지 확인
        
        Returns:
            bool: 키가 설정되어 있으면 True
        """
        return os.getenv("ENCRYPTION_KEY") is not None
