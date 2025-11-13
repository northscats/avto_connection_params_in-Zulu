


class XML:
    def xml_avto_sent_off_house(id, Layer):
        xml_avto_sent_off_house = f"""<?xml version="1.0" encoding="UTF-8"?>
            <zulu-server service="zws" version="1.0.0">
                <Command>
                    <NetworkAnalyzeSwitch>        
                        <Layer>LAYTERS:{Layer}</Layer>   
                    `       <Element>
                                <ElemID>{id}</ElemID>
                                <Mode>2</Mode>
                            </Element>
                    </NetworkAnalyzeSwitch>
                </Command>
            </zulu-server>"""
        return xml_avto_sent_off_house
    def xml_select_data_off_house(id, Layer):
        xml_select_data_off_house = f"""<?xml version="1.0" encoding="UTF-8"?>
            <zulu-server service="zws" version="1.0.0">
                <Command>
                    <LayerExecSql>
                        <Layer>LAYTERS:{Layer}</Layer>
                        <Query>SELECT Geometry.AsText() WHERE sys = {id}</Query>
                        <CRS>EPSG:4326</CRS>
                    </LayerExecSql>
                </Command>
            </zulu-server>"""
        return xml_select_data_off_house
        