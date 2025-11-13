import asyncio
import aiohttp
import random
import logging
from app.api.api_avto_conection_params import settings
from app.XML.xml_avto_conection_params import XML
import xml.etree.ElementTree as ET
import logging
from app.worker.avto_sent_off_house import avto_sent_off_house, avto_select_data_off_house
logger = logging.getLogger(__name__)

from datetime import datetime


shutting_down = False

def jitter(base: float) -> float:
    return base / 2 + random.random() * base


async def post_sql_to(xml_sql):
    url = settings.API_URL_POST_SQL
    auth = aiohttp.BasicAuth(login=settings.API_LOGIN, password=settings.API_PASSWORD)
    async with aiohttp.ClientSession(auth=auth) as session:
        headers ={
            "Content-Type": "application/xml"
        }
        xml_checkList = xml_sql
        try:
            async with session.post(url, data=xml_checkList, headers=headers, timeout=3) as resp:
                resp.raise_for_status()
                data = await resp.text()
                logger.info(f"Успешный POST-запрос: {parse_records_xml(data)}")
        except Exception as e:
                logger.error(f"Другая ошибка: {e}")
    return parse_records_xml(data)

def parse_records_xml(xml_string: str) -> list[dict]:
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

async def choose_layers_seti(type, id):
    if type not in ["ВС", "ТС", "ВО"]:
        return []

    search_data = await search_from_id(type, id)
    logger.info(f"Результат для {type} ({id}): {search_data}")
    return search_data

async def search_from_id(type_to_search: str, id_to_search: str):
    layer_map = {
        "ВО": "vo_mo",
        "ВС": "vs_mo",
        "ТС": "TS_MO",
    }
    layer_name = layer_map.get(type_to_search)
    if not layer_name:
        logger.error(f"Неизвестный тип аварии: {type_to_search}")
        return None
    post_sql_to_seti_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
    <zulu-server service="zws" version="1.0.0">
        <Command>
            <LayerExecSql>
                <Layer>LAYTERS:{layer_name}</Layer>
                <Query>SELECT End_uch, Begin_uch, Nist, Dpod, Dobr, Owner, Proklad WHERE sys = {int(id_to_search)}</Query>
                <CRS>EPSG:4326</CRS>
            </LayerExecSql>
        </Command>
    </zulu-server>"""
    result_post_sql_to_seti = await post_sql_to(post_sql_to_seti_XML)
    return result_post_sql_to_seti



async def update_attributes_checklist(result_post_sql_to_seti: dict, sys_id: str):
    Nach = result_post_sql_to_seti[0].get('Begin_uch', 0)
    Konec = result_post_sql_to_seti[0].get('End_uch', 0)
    NoIst = result_post_sql_to_seti[0].get('Nist', 0)
    Vnut_pod_diametr = result_post_sql_to_seti[0].get('Dpod', 0)
    Vnut_obr_diam = result_post_sql_to_seti[0].get('Dobr', 0)
    Balans = result_post_sql_to_seti[0].get('Owner', 0)
    Vid_proklad = result_post_sql_to_seti[0].get('Proklad', 0)
    post_updateElement_checkList_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
        <zulu-server service="zws" version="1.0.0">
            <Command>
                <UpdateElemAttributes>
                    <Layer>LAYTERS:Чек-лист_УТС_ТС_2025_новый</Layer>
                    <Element>
                        <Key>
                            <Name>Sys</Name>
                            <Value>{int(sys_id)}</Value>
                        </Key>
                        <Field>
                            <Name>Nach</Name>
                            <Value>{Nach}</Value>
                        </Field>
                        <Field>
                            <Name>Konec</Name>
                            <Value>{Konec}</Value>
                        </Field>
                        <Field>
                            <Name>NoIst</Name>
                            <Value>{NoIst}</Value>
                        </Field>
                        <Field>
                            <Name>Vnut_pod_diametr</Name>
                            <Value>{Vnut_pod_diametr}</Value>
                        </Field>
                        <Field>
                            <Name>Vnut_obr_diam</Name>
                            <Value>{Vnut_obr_diam}</Value>
                        </Field>
                        <Field>
                            <Name>Balans</Name>
                            <Value>{Balans}</Value>
                        </Field>
                        <Field>
                            <Name>Vid_proklad</Name>
                            <Value>{Vid_proklad}</Value>
                        </Field>
                    </Element>
                </UpdateElemAttributes>
            </Command>
        </zulu-server>"""
    url = settings.API_URL_POST_UPDATE_ELEMENT
    auth = aiohttp.BasicAuth(login=settings.API_LOGIN, password=settings.API_PASSWORD)
    async with aiohttp.ClientSession(auth=auth) as session:
        headers ={
            "Content-Type": "application/xml"
        }
        xml_checkList = post_updateElement_checkList_XML
        try:
            async with session.post(url, data=xml_checkList, headers=headers, timeout=3) as resp:
                resp.raise_for_status()
        except Exception as e:
                logger.error(f"Другая ошибка: {e}")


async def avto_conection_params():
    processed_ids = set()
    async with aiohttp.ClientSession() as session:
        while not shutting_down:
            try:
                records = await post_sql_to(XML.post_sql_to_checkList_XML)
                new_records = [r for r in records if r["SYS"] not in processed_ids]
                logger.info(f"Получено {len(records)} записей, новых: {len(new_records)}")
                await asyncio.sleep(3)
                backoff = 3
                while new_records:
                    record = new_records.pop(0)
                    logger.info(f"Обработка записи: {record}") 
                    try:
                        result_search_object = await choose_layers_seti(
                            record["Тип_аварии"], record["SYS_obj"]
                        )
                        await update_attributes_checklist(result_search_object, record["SYS"])
                        processed_ids.add(record["SYS"]) 
                        # моделирование
                        layer_map = {
                            "ВО": "vo_mo",
                            "ВС": "vs_mo",
                            "ТС": "TS_MO",
                        }
                        layer_name = layer_map.get(record["Тип_аварии"])
                        dict_off_id = await avto_sent_off_house(record["SYS_obj"], layer_name)
                        array_off_id = []
                        for item in dict_off_id:          
                            for k, v in item.items():      
                                array_off_id.append(int(k))
                                array_off_id.append(int(v))
                        logger.info(f"id отключенных объектов{array_off_id}")
                        array_data_off_house = []
                        json_data = {
                            "metadata": {
                                "timestamp": datetime.now().isoformat(),
                                "sys_obj": record["SYS_obj"],
                                "tip_avarii": record["Тип_аварии"],
                                "total_objects": len(array_off_id)
                            },
                            "otklyuchennye_doma": []
                        }
                        logger.info(f"Данные аварии{json_data}")
                        for number_id in range(len(array_off_id)):
                            data_house = await avto_select_data_off_house(array_off_id[number_id], layer_name)
                           
                            data_houses = array_data_off_house.append(int(data_house))
                            if data_houses: 
                                for house_data in data_houses:
                                    json_data["otklyuchennye_doma"].append({
                                        "object_id": number_id,
                                        "tip_avarii": record["Тип_аварии"],
                                        "data_doma": house_data
                                    })
                        logger.error(data_houses)
                        # моделирование
                        logger.info(f"SYS={record['SYS']} обработан и исключен из повторной обработки")
                    except Exception as e:
                        logger.error(f"Ошибка при обработке SYS={record['SYS']}: {e}")
                        await asyncio.sleep(1)

                logger.info("Все новые записи обработаны, ждем появления новых...")
            except Exception as e:
                logger.error(f"Ошибка при обработке SYS={new_records.get('SYS', 'неизвестно')}: {e}")
                await asyncio.sleep(3)
                backoff = 3
                for i in range(5):
                    if shutting_down:
                        break
                    wait = jitter(backoff)
                    logger.warning(f"Retry {i+1}, waiting {wait:.1f}s")
                    await asyncio.sleep(wait)
                    try:
                        await post_sql_to(XML.post_sql_to_checkList_XML)
                        break
                    except Exception:
                        backoff *= 2

            await asyncio.sleep(settings.POLL_INTERVAL)

    logger.info("Background worker stopped.")
