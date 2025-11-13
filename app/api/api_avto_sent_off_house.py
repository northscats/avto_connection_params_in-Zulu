from pydantic_settings import BaseSettings

class class_api_avto_sent_off_house(BaseSettings):
    API_LOGIN: str = "sa"
    API_PASSWORD: str = "AzA$64034073%11524282"

    API_URL_POST_SQL: str = "https://is.arki.mosreg.ru/zws/LayerExecSQL"
    API_URL_POST_NetworkAnalyzeSwitch : str = "https://is.arki.mosreg.ru/zws/NetworkAnalyzeSwitch"
    POLL_INTERVAL: int = 3


object_class_api_avto_sent_off_house = class_api_avto_sent_off_house()
