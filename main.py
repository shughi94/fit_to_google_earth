from garmin_fit_sdk import Decoder, Stream
import simplekml
from datetime import datetime, timedelta
from simplekml import Kml

# read .fit file
stream = Stream.from_file("Activity.fit")
decoder = Decoder(stream)
messages, errors = decoder.read()

IDK_SHIT_CONVERSION = 11930465

coordinates = []
when = []
heartrate = []
speed = []

first_lat = None
first_long = None
first_when = None
end_when = None
first = True

custom_times = []


for record in messages["record_mesgs"]:
    if first:
        first_long = record["position_long"] / IDK_SHIT_CONVERSION
        first_lat = record["position_lat"] / IDK_SHIT_CONVERSION
        first_when = record["timestamp"]
        end_when = first_when + timedelta(minutes=1)
        first = False

    custom_times.append(first_when + timedelta(seconds=0.01))

    # print(record)
    # print(record["timestamp"].strftime("%m/%d/%Y, %H:%M:%S"))
    coordinates.append(
        (
            record["position_long"] / IDK_SHIT_CONVERSION,
            record["position_lat"] / IDK_SHIT_CONVERSION,
            record["enhanced_altitude"],
        )
    )
    when.append(record["timestamp"].strftime("%d/%m/%Y, %H:%M:%S"))
    heartrate.append(record["heart_rate"])
    speed.append(int(record["enhanced_speed"]))

# Create a KML object
kml = simplekml.Kml()

# Create a new point and style it
pnt = kml.newpoint(name="Takeoff", coords=[(first_long, first_lat)])
pnt.style.iconstyle.scale = 0.5

# Create a tour and attach a playlist to it
tour = kml.newgxtour(name="Play me!")
playlist = tour.newgxplaylist()

# Attach a gx:FlyTo to the playlist
flyto = playlist.newgxflyto(gxduration=2)
flyto.camera.longitude = first_long
flyto.camera.latitude = first_lat
flyto.camera.altitude = 10000
flyto.camera.heading = -6.333
flyto.camera.tilt = 5
flyto.camera.roll = 30



count = 0
for triple in coordinates:
    # Attach a gx:AnimatedUpdate to the playlist
    animatedupdate = playlist.newgxanimatedupdate(gxduration=0.1)

    partial_coords = [coordinates[count]]

    ls = kml.newlinestring(name="line")
    ls.extrude = 0
    ls.altitudemode = simplekml.AltitudeMode.absolute
    ls.style.linestyle.width = 2
    ls.style.linestyle.color = simplekml.Color.yellow

    ls.coords = partial_coords
    animatedupdate.update.change = ls.__str__()

    # if count == 5:
    #     break

    count = count + 1

# Attach a gx:Wait to the playlist to give the gx:AnimatedUpdate time to finish
wait = playlist.newgxwait(gxduration=1000)

kml.save("test.kml")

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
