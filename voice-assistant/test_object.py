from services.hand_tracking import HandTrackingService


tracker = HandTrackingService()


image = tracker.capture_hand_region()


print(
    "Captured:",
    image
)