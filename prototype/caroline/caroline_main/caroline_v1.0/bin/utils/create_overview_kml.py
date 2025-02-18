import os
import glob
import json
from datetime import datetime


def read_SLC_json(filename):
    f = open(filename)
    data = json.load(f)
    f.close()
    return data['geometry']['coordinates'][0]


class KML:
    def __init__(self, save_path):
        self.save_path = save_path
        self.kml = ""
        self._prepare_kml()

    def _prepare_kml(self):
        self.kml += """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""
        self._add_kml_styles()

    def _finish_kml(self):
        self.kml += """</Document>
</kml>"""

    def save(self):
        self._finish_kml()
        f = open(self.save_path, "w")
        f.write(self.kml)
        f.close()

    def _add_kml_styles(self):
        self.kml += """    <StyleMap id="SLC">
        <Pair>
            <key>normal</key>
            <styleUrl>#SLC-n</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#SLC-h</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="SLC-n">
        <LineStyle>
            <color>ff0000ff</color>
            <width>1</width>
        </LineStyle>
        <PolyStyle>
            <color>8014B4FF</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="SLC-h">
        <LineStyle>
            <color>ff00ffff</color>
            <width>3</width>
        </LineStyle>
        <PolyStyle>
            <color>5014B4FF</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <StyleMap id="AoI">
        <Pair>
            <key>normal</key>
            <styleUrl>#AoI-n</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#AoI-h</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="AoI-n">
        <LineStyle>
            <color>ff00ff00</color>
            <width>1</width>
        </LineStyle>
        <PolyStyle>
            <color>8078E352</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="AoI-h">
        <LineStyle>
            <color>ff00ffff</color>
            <width>3</width>
        </LineStyle>
        <PolyStyle>
            <color>5078E352</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <StyleMap id="stack">
        <Pair>
            <key>normal</key>
            <styleUrl>#stack-n</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#stack-h</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="stack-n">
        <LineStyle>
            <color>ffff0000</color>
            <width>1</width>
        </LineStyle>
        <PolyStyle>
            <color>80919C8E</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="stack-h">
        <LineStyle>
            <color>ff00ffff</color>
            <width>3</width>
        </LineStyle>
        <PolyStyle>
            <color>50919C8E</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>    
"""

    def open_folder(self, folder_name, folder_description):
        self.kml += f"""<Folder>
    <name>{folder_name}</name>
    <description>{folder_description}</description>
"""

    def close_folder(self):
        self.kml += "</Folder>\n"

    def add_polygon(self, coordinate_list, name, description, style):
        self.kml += f"""<Placemark>
    <name>{name}</name>
    <description>{description}</description>
    <styleUrl>#{style}</styleUrl>
    <Polygon>
        <outerBoundaryIs>
            <LinearRing>
                <coordinates>
"""

        for coordinate in coordinate_list:
            self.kml += f"                  {coordinate[0]},{coordinate[1]}\n"

        self.kml += """             </coordinates>
            </LinearRing>
        </outerBoundaryIs>
    </Polygon>
</Placemark>"""


if __name__ == "__main__":
    # AN EXAMPLE WORKFLOW:
    """
    kml = KML('test.kml')
    kml.open_folder('SLCs', 'Extents of all downloaded SLCs')
    kml.add_polygon([(1, 50), (20, 50), (20, 58), (1, 58), (1, 50)], 'dsc_t037_img1',
                    '2014-01-01 - 2025-02-12 (412 images)', 'SLC')
    kml.close_folder()

    kml.open_folder('Stacks', 'Extents of all processed stacks in CAROLINE')
    kml.add_polygon([(4, 52), (6, 52), (6, 55), (5, 54), (4, 52)], 'nl_limburg',
                    'nl_limburg\ndsc_t037 (last update 2025-01-03 in /project)\nasc_t088 (last update 2025-02-04 in /project)', 'stack')
    kml.close_folder()

    kml.open_folder('AoIs', 'Extents of all AoIs in CAROLINE')
    kml.add_polygon([(5, 53), (6, 53), (6, 54), (5, 54), (5, 53)], 'nl_limburg',
                    'nl_limburg\ndsc_t037 (last update 2025-01-03 in /project)\nasc_t088 (last update 2025-02-04 in /project)', 'AoI')
    kml.close_folder()

    kml.save()
    """

    now = datetime.now()
    now_str = now.strftime("%Y%m%d")

    # kml = KML(f'test_{now_str}.kml')
    kml = KML(f'/project/caroline/Share/caroline-aoi-extents/AoI_summary_{now_str}.kml')
    kml.open_folder('SLCs', 'Extents of all downloaded SLCs')

    # SLC_base_folder = '/Users/sanvandiepen/PycharmProjects/workingEnvironment2/stackswaths'
    SLC_base_folder = '/project/caroline/Data/radar_data/sentinel1'
    SLC_folders = glob.glob(f"{SLC_base_folder}/s1*")

    for SLC_folder in SLC_folders:
        name_pt1 = SLC_folder.split('/')[-1]

        dates = glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/2*")
        dates = [date.split('/')[-1] for date in dates]

        if len(dates) > 0:
            first_date = min(dates)
            last_date = max(dates)
            n_dates = len(dates)
            jsons = list(sorted(glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/{last_date}/*.json")))
            for n, json_file in enumerate(jsons):
                coordinates = read_SLC_json(json_file)

                kml.add_polygon(coordinates, f"{name_pt1}_img{n+1}",
                                f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})', 'SLC')
    kml.close_folder()
    kml.save()



