import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict, Counter
import shutil
import os
import io
import API.utils as utils

folders = ['CCLE Cell Line Gene CNV Profiles', 'CCLE Cell Line Gene Expression Profiles',
           'CCLE Cell Line Gene Mutation Profiles']
numpy_array_name = 'gene_attribute_numpy_array.npy'
cell_lines_numpy = 'cell_lines.npy'
drug_response_database = 'cancer_drug_response'
cell_line_drug_response_collection = 'cell_line_drug_response'
median_values_collection = 'compound_median_resistance'


class OrderedCounter(Counter, OrderedDict):
    pass


def get_s3_data():
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = os.path.join(folder, numpy_array_name)
        cell_lines_filename = os.path.join(folder, cell_lines_numpy)
        s3_file = utils.download_s3(filename)
        s3_file_cells = utils.download_s3(cell_lines_filename)

        if not os.path.exists(filename):
            with open(filename, 'rb') as f_in:
                with open(s3_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    print("COPY")
            print("Downloaded " + filename)

        if not os.path.exists(cell_lines_filename):
            with open(cell_lines_filename, 'rb') as f_in:
                with open(s3_file_cells, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    print("COPY")
            print("Downloaded " + cell_lines_filename)

        print("Downloaded " + folder)


def get_s3_data_locally():
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = os.path.join(folder, numpy_array_name)
        cell_lines_filename = os.path.join(folder, cell_lines_numpy)

        if not os.path.exists(filename):
            utils.download_s3_local(filename)
            print("Downloaded " + filename)

        if not os.path.exists(cell_lines_filename):
            utils.download_s3_local(cell_lines_filename)
            print("Downloaded " + cell_lines_filename)

        print("Downloaded " + folder)


class DrugResponse:
    def __init__(self, client_cell_data, k_neighbors):
        self.average_drug_response = {}
        self.compound_class = {}
        self.get_data_locally()
        self.similar_cells = []
        self.k_neighbors = k_neighbors
        for data in client_cell_data:
            filename = data.filename
            self.filename = filename
            split = filename.split(".")
            split_name = split[0]
            data_feature = split_name.split("_")[-1]
            self.feature = data_feature
            self.prediction(data, k_neighbors)

        result = self.final_result()
        self.result = result

    def get_result(self):
        return self.result

    def prediction(self, patient_data, k_neighbors):
        folder = f'CCLE Cell Line Gene {self.feature} Profiles'
        numpy_filename_data = os.path.join(folder, numpy_array_name)
        numpy_filename_cells = os.path.join(folder, cell_lines_numpy)
        numpy_cell_data = np.load(numpy_filename_data, allow_pickle=True)
        numpy_cells = np.load(numpy_filename_cells, allow_pickle=True)
        data = pd.read_csv(patient_data.file, header=0, index_col=0)
        data_numpy = np.array(np.array(data))
        entry_numpy_2d = np.reshape(data_numpy, (1, data.shape[0]))
        similarity = cosine_similarity(numpy_cell_data[:, :data.shape[0]], entry_numpy_2d)
        similarity_reshape = np.reshape(similarity, (1, similarity.shape[0]))
        similarity_reshape_list = similarity_reshape.tolist()
        similarity_reshape_flaten = similarity_reshape.ravel()
        cell_indicies = np.argpartition(similarity_reshape_flaten, -k_neighbors)[-k_neighbors:]
        similar_cells_numpy = numpy_cells[list(cell_indicies)]
        self.similar_cells.append(list(similar_cells_numpy))

    def final_result(self):
        result = self.similar_cells
        result_flat = [item for sublist in result for item in sublist]
        result_flat_ordered_counter = OrderedCounter(result_flat)
        keys = list(result_flat_ordered_counter)

        result_final = sorted(result_flat_ordered_counter,
                              key=lambda x: (-result_flat_ordered_counter[x], keys.index(x)))

        self.average_drug_response_func(result_final[:self.k_neighbors - 5])
        self.sensitive_resistance()
        return self.compound_class

    def average_drug_response_func(self, cells):
        drug_response_collection = utils.donwload_mongo(drug_response_database, cell_line_drug_response_collection)
        for cell in cells:
            cell_line_data = drug_response_collection.find_one({'cell_line': str(cell)})
            drug_response = cell_line_data['drug_response']
            if not self.average_drug_response:
                self.average_drug_response = drug_response
            else:
                for compound, value in self.average_drug_response.items():
                    if compound in self.average_drug_response and compound in drug_response:
                        self.average_drug_response[compound] = (self.average_drug_response[compound] + drug_response[
                            compound]) / 2

                    if not compound in self.average_drug_response:
                        self.average_drug_response[compound] = drug_response[compound]


    def sensitive_resistance(self):
        median_values = utils.donwload_mongo(drug_response_database, median_values_collection)
        compounds = self.average_drug_response.keys()
        for compound in compounds:
            average = self.average_drug_response[compound]
            median = median_values.find_one({'compound': compound})['ic50']
            if average < median:
                self.compound_class[compound] = 'sensitive'
            else:
                self.compound_class[compound] = 'resistance'

    def get_data_locally(self):
        get_s3_data_locally()

    def get_data(self):
        get_s3_data()


def main(client_cell_data, k_neighbors):
    drug_response = DrugResponse(client_cell_data, k_neighbors)
    return drug_response.get_result()


if __name__ == '__main__':
    main()
