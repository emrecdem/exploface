import unittest
import os
import numpy as np
import pandas as pd
import exploface as ef


FEATURENAME_COL = ef._FEAT_NAME_ID

class TestFunctions(unittest.TestCase):
    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    ##
    def test_info_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")
        
        info_dict = ef.get_info(file_to_read, max_len_col_names=50)

        self.assertEqual(info_dict["number_of_columns"], 40)
        self.assertEqual(info_dict["duration"], 19.9)
        self.assertEqual(info_dict["time_resolution"], 0.1)

    ##
    def test_statistics_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        
        stats_df = ef.get_statistics(file_to_read)

        for au in ['AU01_c', 'AU02_c', 'AU23_c']:
            self.assertEqual(round(stats_df.loc[au, "average_length_detection"], 4), 2.5)
            self.assertEqual(round(stats_df.loc[au, "nr_detections"],4), 2)
            self.assertEqual(round(stats_df.loc[au, "std_average_length_detection"], 4), round(0.7071067811865476,4))

    ##
    def test_get_detection_function(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")
        
        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts)

        self.assertEqual(len(df[FEATURENAME_COL]), 6)
        self.assertEqual(len(set(df[FEATURENAME_COL])), 3)
        self.assertEqual(len(set(df["start"])),2)
        self.assertEqual(len(set(df["end"])),2)

    ##
    def test_column_selection(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", "multiple_active_au_2.csv")

        stats_df = ef.get_statistics(file_to_read, column_selection=["AU23_c"])

        self.assertEqual('AU23_c' in stats_df.index, True )
        self.assertEqual('AU01_c' in stats_df.index, False )
        self.assertEqual('AU02_c' in stats_df.index, False )

        stats_df = ef.get_statistics(file_to_read, column_selection=["niks"])

        self.assertEqual(len(stats_df), 0 )

    ##
    def test_skip_seconds_at_end(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, skip_seconds_at_end=15)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 1  )

    ##
    def test_intensity_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_4.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, intensity_threshold=0.3)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 2  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02_c"]), 2  )

        df = ef.get_detections(ts, intensity_threshold=0.6)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 1  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02_c"]), 1  )

    ##
    def test_time_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, time_threshold=1)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 2  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02_c"]), 2  )

        df = ef.get_detections(ts, time_threshold=2.5)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 1  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02_c"]), 1  )

    ##
    def test_smooth_time_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, smooth_time_threshold=1)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 2  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02_c"]), 2  )

        df = ef.get_detections(ts, smooth_time_threshold=4)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01_c"]), 1  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02_c"]), 1  )


    def test_elan_writer(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
                                    "multiple_active_au_2.csv")

        output_path=os.path.join(
            self.get_test_directory(), "temp_files", "temp_test_file.eaf")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts)
        ef.write_elan_file(df, output_path, ".")
        self.assertTrue(os.path.isfile(output_path))

if __name__ == '__main__':
    unittest.main()