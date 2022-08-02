from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime, TEXT, Enum, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

import enum

# enums
class RefGranularity(enum.Enum):
    character = 1
    word = 2
    sentence = 3
    paragraph = 4

Base = declarative_base()

# data tables
# class Dataset(Base):

#     __tablename__ = "Dataset"

#     # columns
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     version = Column(String)
#     # derived_from_dataset_id = Column(Integer, ForeignKey("Dataset.id"))
#     # derived_from_dataset = relationship("Dataset", backref="derived_from_dataset_id")
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

class Record(Base):

    __tablename__ = "Record"

    # columns
    id = Column(Integer, primary_key=True)
    text = Column(TEXT, nullable=False)
    target = Column(String)
    # dataset_id = Column(Integer, ForeignKey("Dataset.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# transform tables
class Transform(Base):

    __tablename__ = "Transform"

    # columns
    id = Column(Integer, primary_key=True)
    module_name = Column(String)
    class_name = Column(String)
    class_args = Column(String)
    class_kwargs = Column(String)
    callable_name = Column(String)
    callable_args = Column(String)
    callable_kwargs = Column(String)
    callable_is_stochastic = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TransformApplied(Base):

    __tablename__ = "TransformApplied"

    # columns
    id = Column(Integer, primary_key=True)
    input_record_id = Column(Integer, ForeignKey("Record.id"))
    output_record_id = Column(Integer, ForeignKey("Record.id"))
    diff = Column(JSON)
    diff_granularity = Column(Enum(RefGranularity))
    transformation_id = Column(Integer, ForeignKey("Transform.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# model tables
class ModelFramework(Base):

    __tablename__ = "ModelFramework"

    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Model(Base):

    __tablename__ = "Model"

    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    framework_id = Column(Integer, ForeignKey("ModelFramework.id"))
    version = Column(String)
    input_signature = Column(String)
    output_signature = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModelInference(Base):

    __tablename__ = "ModelInference"

    # columns
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("Model.id"))
    input_record_id = Column(Integer, ForeignKey("Record.id"))
    output = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())