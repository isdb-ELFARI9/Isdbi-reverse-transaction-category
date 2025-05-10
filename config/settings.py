import pydantic

class Config(pydantic.BaseSettings):
    embedding_model = "text-embedding-3-small"
    embedding_dimension = 1536
