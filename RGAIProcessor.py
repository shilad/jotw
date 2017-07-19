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
        self.race_data = {}
        race_list = ['black', 'white', 'hispanic', 'east asian', 'south asian', 'native american', 'middle eastern',
                     'not sure', 'other', 'nan']
        self.create_empty_table(self.race_data, race_list)
        self.gender_data = {}
        gender_list = ['man', 'woman', 'non binary', 'not sure', 'nan']
        self.create_empty_table(self.gender_data, gender_list)
        self.age_data = {}
        age_list = ['child', 'young adult', 'middle aged', 'elder', 'nan', 'not sure']
        self.create_empty_table(self.age_data, age_list)
        self.instrument_data = {}
        instrument_list = ['sax', 'trumpet', 'trombone', 'piano', 'voice', 'guitar', 'bass', 'drums', 'other', 'nan', 'multiple']
        self.create_empty_table(self.instrument_data, instrument_list)

        # # creates a list of age pairs that are close enough together for disagreement not to matter
        # self.age_pairs = [['child', 'young adult'], ['middle aged', 'young adult'], ['elder', 'middle aged']]

        # creates a list of URLs deleted for having invalid input from both people, therefore probably not being videos
        self.deleted_urls = []
        self.invalid_input = []  # urls with at least one misspelling or something--deal with these later
        self.agreements = 0
        self.disagreements = 0

    def create_empty_table(self, table_dict, type_list):  # this method could be static; should it be?
        for row in type_list:
            table_dict[row] = {}
            for column in type_list:
                table_dict[row][column] = []

    def compare_value(self, valueA, valueB, dictionary, value_options, url):
        if valueA in value_options and valueB in value_options:
            dictionary[valueA][valueB].append(url)
            if valueA == valueB:
                self.agreements += 1
            else:
                self.disagreements += 1
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
            rowA_url = str(rowA[1][0])
            rowA_race = str(rowA[1][2]).lower().replace('-', ' ').rstrip(' ')
            rowA_gender = str(rowA[1][4]).lower().replace('-', ' ').rstrip(' ')
            rowA_age = str(rowA[1][6]).lower().replace('-', ' ').rstrip(' ')
            rowA_instrument = str(rowA[1][8]).lower().replace('-', ' ').rstrip(' ')

            rowB_url = str(rowB[1][0]).lower().replace('-', ' ').rstrip(' ')
            rowB_race = str(rowB[1][2]).lower().replace('-', ' ').rstrip(' ')
            rowB_gender = str(rowB[1][4]).lower().replace('-', ' ').rstrip(' ')
            rowB_age = str(rowB[1][6]).lower().replace('-', ' ').rstrip(' ')
            rowB_instrument = str(rowB[1][8]).lower().replace('-', ' ').rstrip(' ')

            # actually compare values
            if rowA_url != rowB_url:
                print "Error! Tried to compare data for two different URLs!"
            else:
                self.compare_value(rowA_race, rowB_race, self.race_data, self.race_data.keys(), rowA_url)
                self.compare_value(rowA_gender, rowB_gender, self.gender_data, self.gender_data.keys(), rowA_url)
                self.compare_value(rowA_age, rowB_age, self.age_data, self.age_data.keys(), rowA_url)
                self.compare_value(rowA_instrument, rowB_instrument, self.instrument_data, self.instrument_data.keys(), rowA_url)

    def fill_count_dict(self, input_dict, output_dict):  # this method could also be static; again, should it be?
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
        print "There were", self.agreements, "agreements and", self.disagreements, "disagreements."
        print ""

        print "Disagreements:"
        for dictionary in [processor.race_data, processor.gender_data, processor.age_data, processor.instrument_data]:
            for row_key in dictionary.keys():
                for column_key in dictionary[row_key].keys():
                    curr_list = dictionary[row_key][column_key]
                    if row_key != column_key and len(curr_list) != 0:
                        print row_key, "/", column_key, ":", curr_list

processor = RGAIProcessor('//Users/sen/Desktop/RGAI.csv')
processor.compare_rows()

processor.print_aggregate_info()
