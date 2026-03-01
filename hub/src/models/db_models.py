# SQLAlchemy ORM 모델
# LLD 참조: docs/arch/HLD/DATA_MODEL.md § 2
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# TODO: SharedContent, ContentMetadata, User, ReputationEvent, AccessLog, FLUpdate 구현
