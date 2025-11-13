from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_LOGIN: str = "sa"
    API_PASSWORD: str = "AzA$64034073%11524282"

    API_URL_POST_SQL: str = "https://is.arki.mosreg.ru/zws/LayerExecSQL"
    API_URL_POST_UPDATE_ELEMENT: str = "https://is.arki.mosreg.ru/zws/UpdateElemAttributes"
    POLL_INTERVAL: int = 3


    class Config:
        env_file = ".env"

settings = Settings()
