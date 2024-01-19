from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	# model_config = SettingsConfigDict(env_file='.env.development', env_file_encoding='utf-8')
	GOOGLE_API: str
	PROJECT_NAME: str
	BIGTABLE_INSTANCE_NAME: str
	BIGTABLE_TABLE_NAME: str
	GCP_REGION_NAME: str
	POSTGRES_INSTANCE_NAME: str
	POSTGRES_DB_USERNAME: str
	POSTGRES_DB_PASSWORD: str
	POSTGRES_DB_NAME: str

class BigTableColumnSettings(BaseSettings):
	TRANSACTION_COL_NAME: str
	SESSION_COL_NAME: str
	QUESTION_COL_NAME: str
	ANSWER_COL_NAME: str
	REACTION_COL_NAME: str
