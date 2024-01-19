from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	# model_config = SettingsConfigDict(env_file='.env.development', env_file_encoding='utf-8')
	GOOGLE_API_KEY: str
	PINECONE_API_KEY: str
	PINECONE_API_ENV: str


