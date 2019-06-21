from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
                help="OpenCV object tracker type")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "kcf": cv2.TrackerKCF_create,
    "csrt": cv2.TrackerCSRT_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

tracker = OPENCV_OBJECT_TRACKERS[args["tracker"].lower()]()

ROI = None

if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])

fps = None

print("[INFO] press 'a' to select ROI in the center")
print("[INFO] press 's' to select ROI with the mouse")
print("[INFO] press 'c' to clear ROI")
print("[INFO] press 'q' to quit")

while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break

    frame = imutils.resize(frame, width=600)
    (H, W) = frame.shape[:2]
    if ROI is None:
        crosshair = cv2.rectangle(frame, (int(
            W / 2 - 50), int(H / 2 - 50)), (int(W / 2 + 50), int(H / 2 + 50)), (0, 0, 255), 2)
    if ROI is not None:
        (success, box) = tracker.update(frame)

        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)
            cv2.circle(frame, (int(x + w / 2), int(y + h / 2)),
                       2, (0, 255, 0), -1)
        else:
            crosshair = cv2.rectangle(frame, (int(
            W / 2 - 50), int(H / 2 - 50)), (int(W / 2 + 50), int(H / 2 + 50)), (0, 0, 255), 2)

        fps.update()
        fps.stop()

        info = [
            ("Tracker", args["tracker"], (255,0,0)),
            ("Success", "Yes" if success else "No", (0,255,0) if success else (0,0,255)),
            ("FPS", "{:.2f}".format(fps.fps()), (255,0,0)),
        ]

        for (index, (key, value, color)) in enumerate(info):
            text = "{}: {}".format(key, value)
            cv2.putText(frame, text, (10, H - ((index * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("a"):
        ROI = (W / 2 - 50, H / 2 - 50, 100, 100)
        tracker.init(frame, ROI)
        fps = FPS().start()
    elif key == ord("s"):
        ROI = cv2.selectROI(
            "Frame", frame, fromCenter=False, showCrosshair=False)
        tracker.init(frame, ROI)
        fps = FPS().start()
    elif key == ord("c"):
        ROI = None
    elif key == ord("q"):
        break

if not args.get("video", False):
    vs.stop()

else:
    vs.release()

cv2.destroyAllWindows()
