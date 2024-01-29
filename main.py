from garmin_fit_sdk import Decoder, Stream
import simplekml

# read .fit file
stream = Stream.from_file("Activity.fit")
decoder = Decoder(stream)
messages, errors = decoder.read()

IDK_SHIT_CONVERSION = 11930465

# create kml file
kml = simplekml.Kml()

coords = []


count = 0
for record in messages["record_mesgs"]:
    if count % 2 == 0:
        coords.append(
            (
                record["position_long"] / IDK_SHIT_CONVERSION,
                record["position_lat"] / IDK_SHIT_CONVERSION,
                record["enhanced_altitude"],
            )
        )
    # kml.newpoint(
    #     name="tmp",
    #     coords=[
    #         (
    #             record["position_long"] / IDK_SHIT_CONVERSION,
    #             record["position_lat"] / IDK_SHIT_CONVERSION,
    #             record["enhanced_altitude"],
    #         )
    #     ],
    # )
ls = kml.newlinestring(name="A LineString")
ls.coords = coords
ls.extrude = 0
ls.altitudemode = simplekml.AltitudeMode.absolute
ls.style.linestyle.width = 2
ls.style.linestyle.color = simplekml.Color.yellow

kml.save("para.kml")
