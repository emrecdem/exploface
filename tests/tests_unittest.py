import unittest
import os
import numpy as np
import pandas as pd
import exploface as ef

# This testcase tests for reading in and getting time intervals for
# different items (confidence, different AUs, etcetera). It does
# so using the threshold method.
class TestForGettingActivationTimesWithThreshold(unittest.TestCase):

    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    def test_confidence_video_detect_no_emotion(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_no_emotion.csv"))
        confidence_intervals = ef.getActivationTimes(df, "confidence", threshold=1, method="threshold")

        # Test if the whole video has confidence 1 and this confidence_intervals contains
        # only 1 interval
        self.assertEqual(len(confidence_intervals), 1)
        # The first time element of the interval is the first time element of the video
        self.assertEqual(confidence_intervals[0][0], df["timestamp"].iloc[0])
        # Same for the last
        self.assertEqual(confidence_intervals[0][1], df["timestamp"].iloc[-1])

    def test_success_video_detect_no_emotion(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_no_emotion.csv"))
        success_intervals = ef.getActivationTimes(df, "success", threshold=1, method="threshold")

        # Test if the whole video has confidence 1 and this confidence_intervals contains
        # only 1 interval
        self.assertEqual(len(success_intervals), 1)
        # The first time element of the interval is the first time element of the video
        self.assertEqual(success_intervals[0][0], df["timestamp"].iloc[0])
        # Same for the last
        self.assertEqual(success_intervals[0][1], df["timestamp"].iloc[-1])

    def test_AU01_r_video_detect_no_emotion(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_no_emotion.csv"))
        AU01_r_intervals = ef.getActivationTimes(df, "AU01_r", threshold=1, method="threshold")

        self.assertEqual(len(AU01_r_intervals), 0)


    # For this test the confidence and success are 1 and we see if we detect the AU01_r
    def test_AU01_r_video_detect_AU01_r_time2_4(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_AU01_r_time2_4.csv"))
        AU01_r_intervals = ef.getActivationTimes(df, "AU01_r", threshold=1, method="threshold")

        self.assertEqual(len(AU01_r_intervals), 1)
        self.assertEqual(AU01_r_intervals[0][0], 2)
        # Same for the last
        self.assertEqual(AU01_r_intervals[0][1], 4)

    # For this test the confidence and success are 1 and we see if we detect where AU01_r
    # is 0 using the inverse_threshold parameter
    def test_AU01_r_video_detect_AU01_r_time2_4(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_AU01_r_time2_4.csv"))
        AU01_r_intervals = ef.getActivationTimes(df, "AU01_r", threshold=0.9, method="threshold", inverse_threshold=True)

        self.assertEqual(len(AU01_r_intervals), 2)

        self.assertEqual(AU01_r_intervals[0][0], 0)
        self.assertEqual(AU01_r_intervals[0][1], 1.9)

        self.assertEqual(round(AU01_r_intervals[1][0],1), 4.1)
        self.assertEqual(round(AU01_r_intervals[1][1],1), 19.9)

    # For this test the confidence<=0.5 and the threshold for the confidence 0.8. 
    # We see if we indeed do or do not detect the AU01_r depending on the confidence cut. 
    # AU01_r is 1 somewhere.
    def test_AU01_r_video_detect_AU01_r_time2_4_confidence0(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_AU01_r_time2_4_confidence0.csv"))
        AU01_r_intervals = ef.getActivationTimes(df, "AU01_r", threshold=1, method="threshold")

        self.assertEqual(len(AU01_r_intervals), 0)
        #self.assertEqual(AU01_r_intervals[0][0], 2)

        #self.assertEqual(AU01_r_intervals[0][1], 4)

    # For this test the confidence<=0.5 and threshold for the confidence 0.3. We see if we 
    # indeed do or do not detect the AU01_r depending on the confidence cut. 
    # AU01_r is 1 somewhere and should now be picked up
    def test_AU01_r_video_detect_AU01_r_time2_4_confidence0_2(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_AU01_r_time2_4_confidence0.csv"))
        AU01_r_intervals = ef.getActivationTimes(df, "AU01_r", threshold=1, method="threshold", 
                                                confidence_cut = 0.3)

        self.assertEqual(len(AU01_r_intervals), 1)
        self.assertEqual(AU01_r_intervals[0][0], 2)

        self.assertEqual(AU01_r_intervals[0][1], 4)


# In this test case we will test some smoothing options
# when getting time intervals for different items. For
# example we would like to filter out moments where an 
# AU is detected for only a minutely small time interval.
# Or when one time interval is broken up by small intervals
# which we want to smooth out.
class TestSmoothingActivationTimes(unittest.TestCase):

    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    def test_smoothing_over_small_time_intervals(self):
        df = pd.read_csv(os.path.join(self.get_test_directory(), "data", "detect_AU01_r_with_to_smooth_intervals.csv"))
        AU_intervals = ef.getActivationTimes(df, "AU01_r", 
                                            smooth_over_time_interval = 0.3, 
                                            threshold=1, method="threshold")

        # There is one interval from 2.0-4.0 and three small ones at
        # 0.3, 4.2, 10.7 sec. These last three are all 0.2sec long.
        # So in the end we must only detect one interval
        self.assertEqual(len(AU_intervals), 1)
        # The one interval should be a merger of the 2.0-4.0 and the
        # 4.2-4.4 one, since the distance  between them is <0.3sec.
        self.assertEqual(AU_intervals[0][0], 2.0)
        self.assertEqual(AU_intervals[0][1], 4.4)

if __name__ == '__main__':
    unittest.main()