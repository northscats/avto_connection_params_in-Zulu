import aiohttp
from app.api.api_avto_sent_off_house import object_class_api_avto_sent_off_house
from app.XML.xml_avto_sent_off_house import XML
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

async def avto_sent_off_house(id, layer):
    url = object_class_api_avto_sent_off_house.API_URL_POST_NetworkAnalyzeSwitch
    auth = aiohttp.BasicAuth(login=object_class_api_avto_sent_off_house.API_LOGIN, password=object_class_api_avto_sent_off_house.API_PASSWORD)
    async with aiohttp.ClientSession(auth=auth) as session:
        headers ={
            "Content-Type": "application/xml"
        }
        use_xml_avto_sent_off_house = XML.xml_avto_sent_off_house(id, layer)
        try:
            async with session.post(url, data=use_xml_avto_sent_off_house, headers=headers, timeout=3) as resp:
                resp.raise_for_status()
                data = await resp.text()
        except Exception as e:
                logger.error(f"Другая ошибка: {e}")
    return parse_xml_avto_sent_off_house(data)

async def avto_select_data_off_house(id, layer):
    url = object_class_api_avto_sent_off_house.API_URL_POST_SQL
    auth = aiohttp.BasicAuth(login=object_class_api_avto_sent_off_house.API_LOGIN, password=object_class_api_avto_sent_off_house.API_PASSWORD)
    async with aiohttp.ClientSession(auth=auth) as session:
        headers ={
            "Content-Type": "application/xml"
        }
        use_xml_select_data_off_house = XML.xml_select_data_off_house(id, layer)
        try:
            async with session.post(url, data=use_xml_select_data_off_house, headers=headers, timeout=3) as resp:
                resp.raise_for_status()
                data = await resp.text()
        except Exception as e:
                logger.error(f"Другая ошибка: {e}")
    return parse_xml_select_data_off_house(data)


def parse_xml_avto_sent_off_house(xml_string: str) -> list[dict]:
    root = ET.fromstring(xml_string)
    records = []
    for record in root.findall(".//Elements"):
        record_data = {}
        for field in record.findall(".//Element"):
            elemid = field.find("ElemID")
            record_data[elemid.text] = elemid.text
        if record_data:
            records.append(record_data)
    return records

def parse_xml_select_data_off_house(xml_string: str) -> list[dict]:
    root = ET.fromstring(xml_string)
    records = []
    for record in root.findall(".//Record"):
        record_data = {}
        for field in record.findall(".//Field"):
            name_elem = field.find("Name")
            value_elem = field.find("Value")
            if name_elem is not None and value_elem is not None:
                record_data[name_elem.text] = value_elem.text
        if record_data:
            records.append(record_data)
    return records