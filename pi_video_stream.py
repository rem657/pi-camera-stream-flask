import time
from picamera2 import Picamera2
from threading import Thread
from typing import Tuple, Dict, Any


class PiVideoStream:
    """
    A threaded video stream class for the Raspberry Pi Camera Module 2.

    This class uses the picamera2 library to capture frames in a separate
    thread, allowing for higher framerates and non-blocking reads.
    """

    def __init__(self, resolution: Tuple[int, int] = (640, 480),
                 framerate: int = 32,
                 controls: Dict[str, Any] = None):
        """
        Initializes the video stream.

        :param resolution: The resolution of the video stream, as a tuple (width, height).
        :type resolution: Tuple[int, int]
        :param framerate: The desired framerate of the video stream.
        :type framerate: int
        :param controls: A dictionary of camera controls to set (e.g., {"ExposureTime": 10000}).
        :type controls: Dict[str, Any]
        """
        # Initialize the Picamera2 object
        self.camera = Picamera2()

        # Create a video configuration
        # We use "main" for the primary stream and specify BGR888 format for OpenCV compatibility.
        config = self.camera.create_video_configuration(
            main={"size": resolution, "format": "BGR888"},
            controls={"FrameRate": framerate}
        )
        self.camera.configure(config)

        # Set any additional controls if provided
        if controls:
            self.camera.set_controls(controls)

        # Initialize the frame and the stop flag
        self.frame = None
        self.stopped = False
        self.thread = None

    def start(self) -> 'PiVideoStream':
        """
        Starts the camera and the background thread for reading frames.

        :return: The instance of the PiVideoStream.
        :rtype: PiVideoStream
        """
        # Start the camera
        self.camera.start()

        # Allow the camera to warm up
        time.sleep(1.0)

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self) -> None:
        """
        The main loop of the thread. Continuously captures frames from the camera.
        """
        # Keep looping infinitely until the thread is stopped
        while not self.stopped:
            # Grab the frame from the stream
            self.frame = self.camera.capture_array()

    def read(self) -> 'numpy.ndarray':
        """
        Returns the most recently read frame.

        :return: The current frame as a NumPy array.
        :rtype: numpy.ndarray
        """
        return self.frame

    def stop(self) -> None:
        """
        Signals the thread to stop and cleans up resources.
        """
        # Indicate that the thread should be stopped
        self.stopped = True

        # Wait for the thread to finish
        if self.thread is not None:
            self.thread.join()

        # Stop the camera
        self.camera.stop()
        print("Camera stream stopped.")