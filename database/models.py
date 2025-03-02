from sqlalchemy import Column, Integer, String, Float
from database.setup import Base

class ImageMetadata(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    width = Column(Integer)
    height = Column(Integer)
    depth = Column(Integer)
    time_frames = Column(Integer)
    channels = Column(Integer)
