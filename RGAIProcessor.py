import pandas as pd


class RGAIProcessor():

    def __init__(self, filepath):
        # read the CSV into a dataframe and format the dataframe appropriately
        self.df = pd.read_csv(filepath)
        self.df = self.df.rename(columns={'1-3':'Race Certainty', '1-3.1': 'Gender Certainty', '1-3.2':'Age Certainty',
                                          '1-3.3':'Instrument Certainty'})
        self.df.drop(self.df.columns[11:], axis=1, inplace=True)
        self.df = self.df.sort_values(self.df.columns[0])
        self.df = self.df.reindex()  # on second thought, not sure this line is necessary

        # create dictionaries to store mismatches
        self.race_data = {'black': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'white': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'hispanic': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                       'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'east asian': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                         'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'south asian': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                          'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'native american': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                              'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'middle eastern': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                             'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'not sure': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                       'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'other': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []},
                          'nan': {'black': [], 'white': [], 'hispanic': [], 'east asian': [], 'south asian': [],
                                    'native american': [], 'middle eastern': [], 'not sure': [], 'other': [], 'nan': []}}
        self.gender_data = {'woman': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'man': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'non-binary': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'not sure': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []},
                            'nan': {'woman': [], 'man': [], 'non-binary': [], 'not sure': [], 'nan': []}}
        self.age_data = {'child': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'young adult': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'middle-aged': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'elder': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []},
                         'nan': {'child': [], 'young adult': [], 'middle-aged': [], 'elder': [], 'nan': []}}
        self.instrument_data = {'sax': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                        'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'trumpet': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                            'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'trombone': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                             'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'piano': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'voice': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'guitar': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                           'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'bass': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                         'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'drums': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'other': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                          'bass': [], 'drums': [], 'other': [], 'nan': []},
                                'nan': {'sax': [], 'trumpet': [], 'trombone': [], 'piano': [], 'voice': [], 'guitar': [],
                                        'bass': [], 'drums': [], 'other': [], 'nan': []}}

        # # creates a list of age pairs that are close enough together for disagreement not to matter
        # self.age_pairs = [['child', 'young adult'], ['middle-aged', 'young adult'], ['elder', 'middle-aged']]

        # creates a list of URLs deleted for having invalid input from both people, therefore probably not being videos
        self.deleted_urls = []
        self.invalid_input = []  # urls with at least one misspelling or something--deal with these later

    def compare_value(self, valueA, valueB, dictionary, value_options, url):
        if valueA in value_options and valueB in value_options:
            dictionary[valueA][valueB].append(url)
        else:
            self.invalid_input.append(url)
        if valueA == "nan" and valueB == "nan":
            self.deleted_urls.append(url)

    def compare_rows(self):
        # iterate over even-numbered rows in the dataframe and compare each video to itself
        generator = self.df.iterrows()
        for i in range(0, 500):
            # choose the next two rows, starting at the beginning
            rowA = generator.next()
            rowB = generator.next()

            # pull URL, race, gender, age, and instrument values from their respective cells
            rowA_url = str(rowA[1][0]).lower()
            rowA_race = str(rowA[1][2]).lower()
            rowA_gender = str(rowA[1][4]).lower()
            rowA_age = str(rowA[1][6]).lower()
            rowA_instrument = str(rowA[1][8]).lower()

            rowB_url = str(rowB[1][0]).lower()
            rowB_race = str(rowB[1][2]).lower()
            rowB_gender = str(rowB[1][4]).lower()
            rowB_age = str(rowB[1][6]).lower()
            rowB_instrument = str(rowB[1][8]).lower()

            # actually compare values
            if rowA_url != rowB_url:
                print "Error! Tried to compare data for two different URLs!"
            else:
                self.compare_value(rowA_race, rowB_race, self.race_data, self.race_data.keys(), rowA_url)
                self.compare_value(rowA_gender, rowB_gender, self.gender_data, self.gender_data.keys(), rowA_url)
                self.compare_value(rowA_age, rowB_age, self.age_data, self.age_data.keys(), rowA_url)
                self.compare_value(rowA_instrument, rowB_instrument, self.instrument_data, self.instrument_data.keys(), rowA_url)

    def fill_count_dict(self, input_dict, output_dict):
        for row_key in input_dict.keys():
            output_dict[row_key] = {}
            for column_key in input_dict[row_key].keys():
                output_dict[row_key][column_key] = len(input_dict[row_key][column_key])

    def print_aggregate_info(self):

        race_counts = {}
        gender_counts = {}
        age_counts = {}
        instrument_counts = {}
        self.fill_count_dict(processor.race_data, race_counts)
        self.fill_count_dict(processor.gender_data, gender_counts)
        self.fill_count_dict(processor.age_data, age_counts)
        self.fill_count_dict(processor.instrument_data, instrument_counts)

        race_df = pd.DataFrame(race_counts)
        gender_df = pd.DataFrame(gender_counts)
        age_df = pd.DataFrame(age_counts)
        instrument_df = pd.DataFrame(instrument_counts)
        for frame in [race_df, gender_df, age_df, instrument_df]:
            print frame
            print ""

        print len(self.deleted_urls), "URLs had one or more field in which both inputs were NaN."
        print "People entered non-options for", len(self.invalid_input), "URLs. They were:", self.invalid_input

processor = RGAIProcessor('//Users/sen/Desktop/RGAI.csv')
processor.compare_rows()

processor.print_aggregate_info()
