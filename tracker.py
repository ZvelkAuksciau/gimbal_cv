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
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

ROI = None

if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])

fps = None

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

        fps.update()
        fps.stop()

        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
        ]

        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("a"):
        ROI = (W / 2 - 50, H / 2 - 50, 100, 100)
        tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
        tracker.init(frame, ROI)
        fps = FPS().start()
    elif key == ord("s"):
        ROI = cv2.selectROI(
            "Frame", frame, fromCenter=False, showCrosshair=False)
        tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
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
