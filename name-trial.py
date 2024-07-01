import scrubadub

scrubber = scrubadub.Scrubber()
scrubber.add_detector(scrubadub.detectors.TextBlobNameDetector)
name = scrubber.clean(
    "Profile Name Role Address Syed HarisKosar Ali Software Programmer Bhopal – House no. 10, Baramahal, opposite to Old Civil Court Profile"
)


print(name)
