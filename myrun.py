#!/usr/bin/python3

from garmin_fit_sdk import Decoder, Stream
import datetime
import numpy as np
import sys

if len(sys.argv)<2:
    FIT_File = "Activity.fit"
else:
    FIT_File =  sys.argv[1]

# read .fit file
stream = Stream.from_file(FIT_File)
decoder = Decoder(stream)
messages, errors = decoder.read()

ALTITUDE_ERROR = 15

# envs
coords = []

def calcola_heading(lat1, lon1, lat2, lon2):
    """
    Calcola l'angolo di heading (rotta) in gradi tra due punti GPS.
    I valori di input (latitudine, longitudine) devono essere in gradi.
    Il valore di ritorno (heading) è in gradi, da 0 a 360.
    """

    # Converte i gradi in radianti
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Differenza di longitudine
    delta_lon = lon2_rad - lon1_rad

    # Calcolo del numeratore e del denominatore per atan2
    y = np.sin(delta_lon) * np.cos(lat2_rad)
    x = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(delta_lon)

    # Calcolo dell'angolo in radianti
    initial_bearing = np.atan2(y, x)

    # Converte l'angolo da radianti a gradi e lo normalizza tra 0 e 360
    initial_bearing_deg = np.degrees(initial_bearing)
    heading = (initial_bearing_deg + 360) % 360

    return heading

for record in messages["record_mesgs"]:
    try:
        lat = record['position_lat'] * (180.0 / 2**31)
        lon = record['position_long'] * (180.0 / 2**31)
        ele = record['enhanced_altitude'] + ALTITUDE_ERROR # metri
        ts  = record.get('timestamp')    # datetime
        if isinstance(ts, datetime.datetime):
            ts = ts.isoformat()

        speed = record.get('speed')  # m/s
        hr = record.get('heart_rate')
        coords.append((lon, lat, ele, ts))
    except:
        continue

# Crea un file KML con gx:Track (supporta tempo e quota)
kml_file = "Activity.kml"
with open(kml_file, "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
    f.write("""<kml xmlns="http://www.opengis.net/kml/2.2"
    xmlns:gx="http://www.google.com/kml/ext/2.2">\n""")
    f.write("<Document>\n")
    f.write("  <name>Tour Garmin FlyTo</name>\n")

    f.write('     <Style id="pathStyle">\n')
    f.write("      <IconStyle>\n")
    f.write("        <Icon>\n")
    f.write("          <href>para.png</href>\n")
    f.write("        </Icon>\n")
    f.write("        <scale>1.5</scale>\n")
    f.write("      </IconStyle>\n")
    f.write("        <LabelStyle> <scale>0</scale> </LabelStyle>\n")
    f.write("        <LineStyle>\n")
    f.write("           <color>ff0000ff</color>\n")
    f.write("           <width>4</width>\n")
    f.write("        </LineStyle>\n")
    f.write("     </Style>\n")
    f.write("    <Style><LineStyle><color>ff0000ff</color><width>5</width></LineStyle></Style>\n")
    # gx:Track
    f.write("  <Placemark>\n")
    f.write("    <name>Attività Garmin</name>\n")
    f.write("    <styleUrl>#pathStyle</styleUrl>")
    f.write("    <gx:Track>\n")
    f.write("      <altitudeMode>absolute</altitudeMode>\n")
    for lon, tat, ele, ts in coords:
        f.write(f"      <when>{ts}</when>\n")
        f.write(f"      <gx:coord>{lon} {lat} {ele}</gx:coord>\n")
    f.write("    </gx:Track>\n")
    f.write("  </Placemark>\n")

    f.write("</Document>\n</kml>\n")
    f.close()

print(f"KML tour con FlyTo generato: {kml_file}")

# Crea un file KML con il volo
# gx:Tour con AnimatedUpdate per animazione automatica

kml_file = "Activity_CameraFly.kml"

camera_tilt = 45       # tilt in gradi
camera_range = 0    # distanza camera
camera_heading = 0     # direzione
flyto_interval = 5  # prendi un punto ogni 5 punti per il FlyTo
flyto_duration = 1.0  # durata in secondi tra FlyTo

with open(kml_file, "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
    f.write("""<kml xmlns="http://www.opengis.net/kml/2.2"
    xmlns:gx="http://www.google.com/kml/ext/2.2">\n""")
    f.write("<Document>\n")
    f.write("  <name>Tour Garmin FlyTo</name>\n")

    f.write('     <Style id="pathStyle">\n')
    f.write("      <IconStyle>\n")
    f.write("        <Icon>\n")
    f.write("          <href>para40.png</href>\n")
    f.write("        </Icon>\n")
    f.write("        <scale>1.5</scale>\n")
    f.write("      </IconStyle>\n")
    f.write("        <LabelStyle> <scale>0</scale> </LabelStyle>\n")
    f.write("        <LineStyle>\n")
    f.write("           <color>ff0000ff</color>\n")
    f.write("           <width>4</width>\n")
    f.write("        </LineStyle>\n")
    f.write("     </Style>\n")
    f.write("    <Style><LineStyle><color>ff0000ff</color><width>5</width></LineStyle></Style>\n")

   # gx:Tour con FlyTo multipli
    f.write("  <gx:Tour>\n")
    f.write("    <name>Tour Automatico</name>\n")
    f.write("    <gx:Playlist>\n")

    # FlyTo ogni flyto_interval punti
    for i in range(0, len(coords), flyto_interval):
        lon, lat, ele, *_ = coords[i]
        try:
            lon_next, lat_next, _, _ = coords[i+1]
            camera_heading = calcola_heading(lat, lon, lat_next, lon_next)
        except:
            camera_heading = 0

        f.write("      <gx:FlyTo>\n")
        f.write(f"        <gx:duration>{flyto_duration}</gx:duration>\n")
        f.write("        <gx:flyToMode>smooth</gx:flyToMode>\n")
        f.write("        <Camera>\n")
        f.write(f"          <longitude>{lon}</longitude>\n")
        f.write(f"          <latitude>{lat}</latitude>\n")
        f.write(f"          <altitude>{ele}</altitude>\n")  # altezza camera sopra il terreno
        f.write(f"          <heading>{camera_heading}</heading>\n")
        f.write(f"          <tilt>{camera_tilt}</tilt>\n")
        f.write(f"          <range>{camera_range}</range>\n")
        f.write("          <altitudeMode>absolute</altitudeMode>\n")
        f.write("        </Camera>\n")
        f.write("      </gx:FlyTo>\n")

    f.write("    </gx:Playlist>\n")
    f.write("  </gx:Tour>\n")

    f.write("</Document>\n</kml>\n")

print(f"KML tour della camera generato: {kml_file}")
