class XML:	
    post_sql_to_checkList_XML = """<?xml version="1.0" encoding="UTF-8"?>
	<zulu-server service="zws" version="1.0.0">
	<Command>
		<LayerExecSql>
                <Layer>LAYTERS:Чек-лист_УТС_ТС_2025_новый</Layer>
			    <Query>SELECT SYS, SYS_obj, Тип_аварии WHERE 
                    SYS_obj is NOT NULL 
                    AND Тип_аварии is NOT NULL 
                    AND (Год_ввода_в_эксплуатацию is NULL 
                    OR NoIst is NULL
                    OR Balans is NULL
                    OR Nach is NULL
                    OR Konec is NULL
                    OR Vnut_obr_diam is NULL
                    OR Glub_zaleg is NULL
                    OR Vid_proklad is NULL)
                </Query>
            <CRS>EPSG:4326</CRS>
		</LayerExecSql>
	</Command>
	</zulu-server>"""



