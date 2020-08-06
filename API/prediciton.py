import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import shutil
import os
import utils


folders = ['CCLE Cell Line Gene CNV Profiles', 'CCLE Cell Line Gene Expression Profiles',
           'CCLE Cell Line Gene Mutation Profiles']
numpy_array_name = 'gene_attribute_numpy_array.npy'
cell_lines_numpy = 'cell_lines.npy'


def get_s3_data():
    for folder in folders:
        filename = os.path.join(folder, numpy_array_name)
        cell_lines_filename = os.path.join(folder, cell_lines_numpy)
        s3_file = utils.download_s3(filename)
        s3_file_cells = utils.download_s3(cell_lines_filename)

        if not os.path.exists(folder):
            os.mkdir(folder)

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


class DrugResponse:
    def __init__(self, client_cell_data, k_neighbors):
        get_s3_data()
        self.similar_cells = []
        for data in client_cell_data:
            filename = data.filename
            self.filename = filename
            split = filename.split(".")
            split_name = split[0]
            data_feature = split_name.split("_")[-1]
            self.feature = data_feature
            self.prediction(data, k_neighbors)

    def prediction(self, patient_data, k_neighbors):
        folder = f'CCLE Cell Line Gene {self.feature} Profiles'
        numpy_filename_data = os.path.join(folder, numpy_array_name)
        numpy_filename_cells = os.path.join(folder, cell_lines_numpy)
        numpy_cell_data = np.load(numpy_filename_data)
        numpy_cells = np.load(numpy_filename_cells)
        data = pd.read_csv(patient_data)
        data_numpy = np.array(np.array(data))
        entry_numpy_2d = np.reshape(data_numpy, (1, data.shape[0]))
        similarity = cosine_similarity(numpy_cell_data, entry_numpy_2d)
        similarity_reshape = np.reshape(similarity, (1, similarity.shape[0]))
        similarity_reshape_list = similarity_reshape.tolist()
        similarity_reshape_flaten = similarity_reshape.ravel()
        cell_indicies = np.argpartition(similarity_reshape_flaten, -k_neighbors)[-k_neighbors:]
        similar_cells_numpy = numpy_cells[list(cell_indicies)]
        self.similar_cells.append(similar_cells_numpy)




def main(client_cell_data):

    DrugResponse(client_cell_data)

if __name__ == '__main__':
    main()