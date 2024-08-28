from garmin_fit_sdk import Decoder, Stream
import simplekml
from datetime import datetime, timedelta
from simplekml import Kml


# ------VARIABLES-----------

PERCENTAGE_OF_LINE = 50
ALTITUDE_ERROR = 0

# -----------------------


NO_IDEA_SHIT_CONVERSION = 11930465

# read .fit file
stream = Stream.from_file("Activity.fit")
decoder = Decoder(stream)
messages, errors = decoder.read()

# envs
coordinates = []
when = []
heartrate = []
speed = []

first_lat = None
first_long = None
first_when = None
end_when = None
first = True

custom_times = [] #TODO


percentage = int(len(messages["record_mesgs"]) * (PERCENTAGE_OF_LINE / 100))
count = 0

for record in messages["record_mesgs"]:
    try:
        if first:
            first_long = record["position_long"] / NO_IDEA_SHIT_CONVERSION
            first_lat = record["position_lat"] / NO_IDEA_SHIT_CONVERSION
            first_when = record["timestamp"]
            end_when = first_when + timedelta(minutes=1)
            first = False

        custom_times.append(first_when + timedelta(seconds=0.01))

        # print(record)
        # print(record["timestamp"].strftime("%m/%d/%Y, %H:%M:%S"))
        coordinates.append(
            (
                record["position_long"] / NO_IDEA_SHIT_CONVERSION,
                record["position_lat"] / NO_IDEA_SHIT_CONVERSION,
                record["enhanced_altitude"] + ALTITUDE_ERROR,
            )
        )
        when.append(record["timestamp"].strftime("%d/%m/%Y, %H:%M:%S"))
        heartrate.append(record["heart_rate"])
        speed.append(int(record["enhanced_speed"]))
    except:
        continue
    count = count + 1
    if count > percentage:
        break

# # Create the KML document
working_simple = Kml(name="working_simple", open=1)
lis = working_simple.newlinestring(name="A LineString")
lis.coords = coordinates
lis.extrude = 0
lis.altitudemode = simplekml.AltitudeMode.absolute
lis.style.linestyle.width = 2
lis.style.linestyle.color = simplekml.Color.yellow

# # Save the kml to file
working_simple.save("working_simple.kml")
