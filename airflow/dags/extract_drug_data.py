import pandas as pd
import numpy as np
import pymongo
import shutil
import gzip
import os
import utils

drug_data_name = 'CCLE_Drug_Data.csv'
folders = ['CCLE Cell Line Gene CNV Profiles', 'CCLE Cell Line Gene Expression Profiles',
           'CCLE Cell Line Gene Mutation Profiles']
matrix_zip = 'gene_attribute_matrix.txt.gz'
matrix_txt = 'gene_attribute_matrix.txt'
numpy_array_name = 'gene_attribute_numpy_array.npy'
cell_lines_numpy = 'cell_lines.npy'
mongo_database = "cancer_drug_response"
mongo_collection = "cell_line_drug_response"


def save_patient_folders_s3():
    for j in range(1, 7):
        folder = "Patient_" + str(j)
        patient_data = os.listdir(folder)
        for data in patient_data:
            file = os.path.join(folder, data)
            print("Uploading " + file + " \n...")
            utils.upload_s3(file)
            print("Uploaded " + file)


class CellData:
    def __init__(self, cell_data_file_name_zip, folder, drug_data):
        self.folder = folder
        split = folder.split(" ")
        feature = split[-2]
        self.feature = feature
        download_file_s3_name = utils.download_s3(cell_data_file_name_zip)
        cell_data = self._decompress(download_file_s3_name, cell_data_file_name_zip)
        numpy_array = self.cell_lines_with_drug_data(cell_data, drug_data)
        self.save_numpy_array_s3(numpy_array, numpy_array_name)

    def _decompress(self, filename, s3_path):
        txt_file = s3_path.rsplit(".", 1)[0]
        print("Text File: " + txt_file)
        if os.path.isfile(txt_file):
            print("File Exists")
        else:
            os.mkdir(self.folder)
            with gzip.open(filename, 'rb') as f_in:
                with open(txt_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    print("COPY")
        data = pd.read_csv(txt_file, sep='\t', lineterminator='\n',
                           error_bad_lines=False
                           )
        print(data.head())
        return data

    def cell_lines_with_drug_data(self, cell_data, drug_data):
        cells = cell_data.columns
        cells = cells[3:]

        cells_from_drug_data = list(drug_data["Cell Line"])
        cell_lines_without_data = [w for w in cells if w not in cells_from_drug_data]
        cell_lines_without_data = list(cell_lines_without_data)
        cell_with_drug_data = cell_data.loc[:, ~cell_data.columns.isin(cell_lines_without_data)]
        cell_lines_without = cell_data.loc[:, cell_data.columns.isin(cell_lines_without_data)]
        self.cell_line_test_data(cell_lines_without)

        cell_with_drug_data = cell_with_drug_data.set_index("#")

        cell_with_drug_data_cleaned = cell_with_drug_data.iloc[2:, 2:]
        cell_with_drug_data_cleaned_t = cell_with_drug_data_cleaned.T
        cell_with_drug_data_cleaned_t_cells = cell_with_drug_data_cleaned_t.index
        cell_with_drug_data_cleaned_t_cells_numpy = cell_with_drug_data_cleaned_t_cells.to_numpy()
        self.save_numpy_array_s3(cell_with_drug_data_cleaned_t_cells_numpy, cell_lines_numpy)
        cell_with_drug_data_cleaned_t_numpy = cell_with_drug_data_cleaned_t.to_numpy()

        return cell_with_drug_data_cleaned_t_numpy

    def cell_line_test_data(self, cell_lines_without):
        j = 1
        for i in range(3, 10):
            patient_folder = "Patient_" + str(j)
            j += 1
            if not os.path.exists(patient_folder):
                os.mkdir(patient_folder)
            patient_data = cell_lines_without.iloc[2:, i]
            filename = "gene_" + self.feature + ".csv"
            patient_data.to_csv(os.path.join(patient_folder, filename))

    def save_numpy_array_s3(self, numpy_array, numpy_name):
        filename = os.path.join(self.folder, numpy_name)
        if os.path.exists(filename):
            print("Exists")
        else:
            with open(filename, 'wb') as f:
                print("Saving")
                np.save(f, numpy_array)
        print("Uploading")
        utils.upload_s3(filename)


class DrugData:
    def __init__(self, drug_data):
        drug_data_clean = self.clean_drug_data(drug_data)
        self.cell_drug_data(drug_data_clean)

    def clean_drug_data(self, drug_data):
        drug_data_clean = drug_data[["CCLE Cell Line Name", "Compound", "IC50 (uM)"]]
        cell_lines_drug_data_clean = drug_data_clean["CCLE Cell Line Name"]
        cell_line_names = []
        tissues = []
        for cell in cell_lines_drug_data_clean:
            split = cell.split("_")
            cell_line_names.append(split[0])
            tissues.append(" ".join(split[1:]).lower())

        new_data = pd.DataFrame(
            list(zip(cell_line_names, tissues, drug_data_clean["Compound"], drug_data_clean["IC50 (uM)"])),
            columns=["Cell Line", "Tissue", "Compound", "IC50 (uM)"])
        new_data.to_csv("Clean_" + drug_data_name)
        utils.upload_s3("Clean_" + drug_data_name)
        return new_data

    def cell_drug_data(self, drug_data):
        cell_lines = set(drug_data["Cell Line"])
        compounds = drug_data[["Compound", "IC50 (uM)", "Cell Line"]]
        compounds_pivot = compounds.pivot_table(values="IC50 (uM)", index=["Cell Line"], columns="Compound")
        compounds_pivot = compounds_pivot.fillna(compounds_pivot.median())
        drugs = []

        for cell in cell_lines:
            data_with_cell = drug_data.loc[drug_data['Cell Line'] == cell]
            tissue = data_with_cell['Tissue'].iloc[0]
            drug_response = pd.Series(data_with_cell["IC50 (uM)"].values, index=data_with_cell.Compound).to_dict()
            cell_drug = {
                "cell_line": str(cell),
                "tissue": str(tissue),
                "drug_response": drug_response
            }
            drugs.append(cell_drug)

        utils.upload_mongo(mongo_database, mongo_collection, drugs)
        self.median_values(compounds_pivot)

    def median_values(self, compounds_pivot):

        compounds_pivot_median = compounds_pivot.median()
        drugs_median = []

        for i, v in compounds_pivot_median.iteritems():
            median_value = {
                "compound": str(i),
                "ic50": float(v)
            }
            drugs_median.append(median_value)

        utils.upload_mongo(mongo_database, "compound_median_resistance", drugs_median)


def main():
    drug_data_csv = utils.download_s3(drug_data_name)
    drug_data = pd.read_csv(drug_data_csv)
    drug_data_inst = DrugData(drug_data)
    clean_drug_data = drug_data_inst.clean_drug_data(drug_data)
    for folder in folders:
        cell_data_s3_name_zip = os.path.join(folder, matrix_zip)
        CellData(cell_data_s3_name_zip, folder, clean_drug_data)
    #save_patient_folders_s3()


if __name__ == '__main__':
    main()
