from sqlalchemy import Column, Integer, String, JSON, LargeBinary
from database.setup import Base

class Images(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    image = Column(LargeBinary)
    image_metadata = Column(JSON)
    image_attr = Column(JSON, nullable=True)
    analysis_result = Column(JSON, nullable=True)