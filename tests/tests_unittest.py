import unittest
import os
import numpy as np
import pandas as pd
import exploface as ef


FEATURENAME_COL = ef._FEAT_NAME_ID
class TestFunctionsAnalysis(unittest.TestCase):


    def get_test_directory(self):
        return os.path.dirname(os.path.abspath(__file__))

    def test_compare_detection_tables(self):
        file_to_read_1 = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")
        file_to_read_2 = os.path.join(self.get_test_directory(), "data", "multiple_active_au.csv")

        ts = ef.get_feature_time_series(file_to_read_1)
        det_df_1 = ef.get_detections(ts, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )
        
        ts = ef.get_feature_time_series(file_to_read_2)
        det_df_2 = ef.get_detections(ts, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        found, total, overlap_start = \
            ef.analysis.find_overlap(det_df_1, det_df_2, \
                                    "AU01", "AU01", room=1.0,
                                    key_index=FEATURENAME_COL)

        self.assertEqual(found, 1)
        self.assertEqual(total, 1)

    def test_compare_detection_tables_shifts(self):
        file_to_read_1 = os.path.join(self.get_test_directory(), "data", "multiple_active_au_no_shift.csv")
        file_to_read_2 = os.path.join(self.get_test_directory(), "data", "multiple_active_au_shift1.csv")
        file_to_read_3 = os.path.join(self.get_test_directory(), "data", "multiple_active_au_shift2p5.csv")
        
        ts = ef.get_feature_time_series(file_to_read_1)
        det_df = ef.get_detections(ts, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        ts = ef.get_feature_time_series(file_to_read_2)
        det_df_2 = ef.get_detections(ts, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )

        ts = ef.get_feature_time_series(file_to_read_3)
        det_df_3 = ef.get_detections(ts, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    )


        found, total, overlap_start = \
            ef.analysis.find_overlap(det_df, det_df_2, "AU01", "AU01", room=0, key_index=FEATURENAME_COL)
        self.assertEqual(found, 2)
        self.assertEqual(total, 2)

        found, total, overlap_start = \
            ef.analysis.find_overlap(det_df, det_df_3, "AU01", "AU01", room=0.49, key_index=FEATURENAME_COL)
        self.assertEqual(found, 0)
        self.assertEqual(total, 2)

        found, total, overlap_start = \
            ef.analysis.find_overlap(det_df, det_df_3, "AU01", "AU01", room=0.5, key_index=FEATURENAME_COL)
        self.assertEqual(found, 2)
        self.assertEqual(total, 2)


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

        for au in ['AU01', 'AU02', 'AU23']:
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

        stats_df = ef.get_statistics(file_to_read, column_selection=["AU23"])

        self.assertEqual('AU23' in stats_df.index, True )
        self.assertEqual('AU01' in stats_df.index, False )
        self.assertEqual('AU02' in stats_df.index, False )

        stats_df = ef.get_statistics(file_to_read, column_selection=["niks"])

        self.assertEqual(len(stats_df), 0 )

    ##
    def test_skip_seconds_at_end(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, skip_seconds_at_end=15)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 1  )

    ##
    def test_uncertainty_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_3_low_confidence.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, uncertainty_threshold=0.4)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 2  )

        df = ef.get_detections(ts, uncertainty_threshold=1.0)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 1  )

    ##
    def test_intensity_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_4.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, intensity_threshold=0.3)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 2  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02"]), 2  )

        df = ef.get_detections(ts, intensity_threshold=0.6)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 1  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02"]), 1  )

    ##
    def test_time_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, time_threshold=1)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 2  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02"]), 2  )

        df = ef.get_detections(ts, time_threshold=2.5)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 1  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02"]), 1  )

    ##
    def test_smooth_time_threshold(self):
        file_to_read = os.path.join(self.get_test_directory(), "data", \
            "multiple_active_au_2.csv")

        ts = ef.get_feature_time_series(file_to_read)
        df = ef.get_detections(ts, smooth_time_threshold=1)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 2  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02"]), 2  )

        df = ef.get_detections(ts, smooth_time_threshold=4)
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU01"]), 1  )
        self.assertEqual( len(df[df[FEATURENAME_COL]=="AU02"]), 1  )


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