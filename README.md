# Gimbal Computer Vision

This project uses OpenCV python package to track selected objects.

## Requirements

- Python 3
- imutils
- numpy
- opencv-python
- opencv-contrib-python

## Usage

```
python3 tracker.py [-v VIDEO] [-t TRACKER]
```

Optional arguments:

- `-v VIDEO`: path to video file
- `-t TRACKER`: tracker name

## Trackers overview

### BOOSTING

This tracker is based on an online version of AdaBoost — the algorithm that the HAAR cascade based face detector uses internally. This classifier needs to be trained at runtime with positive and negative examples of the object. The initial bounding box supplied by the user ( or by another object detection algorithm ) is taken as the positive example for the object, and many image patches outside the bounding box are treated as the background. Given a new frame, the classifier is run on every pixel in the neighborhood of the previous location and the score of the classifier is recorded. The new location of the object is the one where the score is maximum. So now we have one more positive example for the classifier. As more frames come in, the classifier is updated with this additional data.

**Pros:** None. This algorithm is a decade old and works ok, but I could not find a good reason to use it especially when other advanced trackers (MIL, KCF) based on similar principles are available.

**Cons:** Tracking performance is mediocre. It does not reliably know when tracking has failed.

### MIL

This tracker is similar in idea to the BOOSTING tracker described above. The big difference is that instead of considering only the current location of the object as a positive example, it looks in a small neighborhood around the current location to generate several potential positive examples. You may be thinking that it is a bad idea because in most of these “positive” examples the object is not centered.

This is where Multiple Instance Learning ( MIL ) comes to rescue. In MIL, you do not specify positive and negative examples, but positive and negative “bags”. The collection of images in the positive bag are not all positive examples. Instead, only one image in the positive bag needs to be a positive example! In our example, a positive bag contains the patch centered on the current location of the object and also patches in a small neighborhood around it. Even if the current location of the tracked object is not accurate, when samples from the neighborhood of the current location are put in the positive bag, there is a good chance that this bag contains at least one image in which the object is nicely centered.

**Pros:** The performance is pretty good. It does not drift as much as the BOOSTING tracker and it does a reasonable job under partial occlusion. If you are using OpenCV 3.0, this might be the best tracker available to you. But if you are using a higher version, consider KCF.

**Cons:** Tracking failure is not reported reliably. Does not recover from full occlusion.

### KCF

KFC stands for **Kernelized Correlation Filters**. This tracker builds on the ideas presented in the previous two trackers. This tracker utilizes that fact that the multiple positive samples used in the MIL tracker have large overlapping regions. This overlapping data leads to some nice mathematical properties that is exploited by this tracker to make tracking faster and more accurate at the same time.

**Pros:** Accuracy and speed are both better than MIL and it reports tracking failure better than BOOSTING and MIL. If you are using OpenCV 3.1 and above, I recommend using this for most applications.

**Cons:** Does not recover from full occlusion. Not implemented in OpenCV 3.0.

### TLD

TLD stands for **Tracking, learning and detection**. As the name suggests, this tracker decomposes the long term tracking task into three components — (short term) tracking, learning, and detection. From the author’s paper, “The tracker follows the object from frame to frame. The detector localizes all appearances that have been observed so far and corrects the tracker if necessary. The learning estimates detector’s errors and updates it to avoid these errors in the future.” This output of this tracker tends to jump around a bit. For example, if you are tracking a pedestrian and there are other pedestrians in the scene, this tracker can sometimes temporarily track a different pedestrian than the one you intended to track. On the positive side, this track appears to track an object over a larger scale, motion, and occlusion. If you have a video sequence where the object is hidden behind another object, this tracker may be a good choice.

**Pros:** Works the best under occlusion over multiple frames. Also, tracks best over scale changes.

**Cons:** Lots of false positives making it almost unusable.

### MEDIANFLOW

Internally, this tracker tracks the object in both forward and backward directions in time and measures the discrepancies between these two trajectories. Minimizing this ForwardBackward error enables them to reliably detect tracking failures and select reliable trajectories in video sequences.

In my tests, I found this tracker works best when the motion is predictable and small. Unlike, other trackers that keep going even when the tracking has clearly failed, this tracker knows when the tracking has failed.

**Pros:** Excellent tracking failure reporting. Works very well when the motion is predictable and there is no occlusion.

**Cons:** Fails under large motion.

### GOTURN

Out of all the tracking algorithms in the tracker class, this is the only one based on Convolutional Neural Network (CNN). From OpenCV documentation, we know it is “robust to viewpoint changes, lighting changes, and deformations”. But it does not handle occlusion very well.

### MOSSE

Minimum Output Sum of Squared Error (MOSSE) uses adaptive correlation for object tracking which produces stable correlation filters when initialized using a single frame. MOSSE tracker is robust to variations in lighting, scale, pose, and non-rigid deformations. It also detects occlusion based upon the peak-to-sidelobe ratio, which enables the tracker to pause and resume where it left off when the object reappears. MOSSE tracker also operates at a higher fps (450 fps and even more). To add to the positives, it is also very easy to implement, is as accurate as other complex trackers and much faster. But, on a performance scale, it lags behind the deep learning based trackers.

### CSRT

In the Discriminative Correlation Filter with Channel and Spatial Reliability (DCF-CSR), we use the spatial reliability map for adjusting the filter support to the part of the selected region from the frame for tracking. This ensures enlarging and localization of the selected region and improved tracking of the non-rectangular regions or objects. It uses only 2 standard features (HoGs and Colornames). It also operates at a comparatively lower fps (25 fps) but gives higher accuracy for object tracking.
