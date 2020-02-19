#author @t_sanf / @sharm

from parsing_VOI import *
import pydicom
import math
import nibabel
import re
#import dicom2nifti
import shutil
import SimpleITK as sitk
import pydicom as dicom
import os
import numpy as np

class Dicom2Nifti():

    def __init__(self):
        self.basePATH = r'M:/Stephanie_Harmon/Projects_MRI/test_new_anon_pipeline'
        self.databases=['batch4']
        self.resample = True #this flag will make a directory with resampled images to 1x1x1

    def dicom_to_nifti(self,t2_only=True):
        '''
        convert all dicom files in each database to .nifti format
        :return:
        '''

        databases = self.databases

        if t2_only==True:
            series_all=['t2']
        else:
            series_all=['t2','adc','highb']

        exception_logger=[]
        for database in databases:
            ptlist = self.check_for_nifti_completion()
            #print(ptlist)
            for patient in self.check_for_nifti_completion():
                print("converting files to nifti for patient {}".format(patient))

                #make nifti file if one does not already exist
                if not os.path.exists(os.path.join(self.basePATH, database, patient,'nifti')):
                    os.mkdir(os.path.join(self.basePATH, database, patient,'nifti'))

                for series in series_all:
                    dicom_name = series
                    nifti_name = series

                    #make folder if not already made:
                    if not os.path.exists(os.path.join(self.basePATH,database,patient,'nifti',nifti_name)):
                        os.mkdir(os.path.join(self.basePATH,database,patient,'nifti',nifti_name))

                    dicom_directory=os.path.join(self.basePATH,database,patient,'dicoms',dicom_name)
                    nifti_directory=os.path.join(self.basePATH, database, patient, 'nifti', nifti_name)
                    try:
                        if series == 't2':
                            self.Dicom_series_Reader(dicom_directory, nifti_directory, nifti_name + '.nii.gz')

                        if series == 'adc' or series == 'highb':
                            filter = self.dicom_series_define_reference(os.path.join(self.basePATH,database,patient,'dicoms','t2'))
                            self.Dicom_series_Reader_withReference(dicom_directory, nifti_directory,nifti_name+'.nii.gz',filter)
                    except:
                        print('error for ' + dicom_directory)

        print("the following patients still need to be processed {}".format(exception_logger))

    def Dicom_series_Reader(self,Input_path, Output_path, savename):
        #print("Reading Dicom directory:", Input_path)
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(Input_path)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        sitk.WriteImage(image, os.path.join(Output_path,savename))
        if self.resample == True:
            new_spacing = [1, 1, 1]
            orig_size = np.array(image.GetSize(), dtype=np.int)
            orig_spacing = np.array(image.GetSpacing())
            new_size = orig_size * (orig_spacing / new_spacing)
            new_size = np.ceil(new_size).astype(np.int)  # Image dimensions are in integers
            new_size = [int(s) for s in new_size]

            resample = sitk.ResampleImageFilter()
            resample.SetInterpolator = sitk.sitkLinear
            resample.SetOutputSpacing(new_spacing)
            resample.SetSize(new_size)
            resample.SetOutputDirection(image.GetDirection())
            resample.SetOutputOrigin(image.GetOrigin())
            new_image = resample.Execute(image)
            sitk.WriteImage(new_image, os.path.join(Output_path,str.replace(savename,'.nii.gz','_resampled.nii.gz')))



    def dicom_series_define_reference(self,Input_path):
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(Input_path)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        Filter = sitk.ResampleImageFilter()
        Filter.SetReferenceImage(image)
        return Filter

    def Dicom_series_Reader_withReference(self,Input_path, Output_path, savename, Filter):
        #print("Reading Dicom directory:", Input_path)
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(Input_path)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        image = Filter.Execute(image)
        sitk.WriteImage(image, os.path.join(Output_path,savename))

        if self.resample == True:
            new_spacing = [1, 1, 1]
            orig_size = np.array(image.GetSize(), dtype=np.int)
            orig_spacing = np.array(image.GetSpacing())
            new_size = orig_size * (orig_spacing / new_spacing)
            new_size = np.ceil(new_size).astype(np.int)  # Image dimensions are in integers
            new_size = [int(s) for s in new_size]

            resample = sitk.ResampleImageFilter()
            resample.SetInterpolator = sitk.sitkLinear
            resample.SetOutputSpacing(new_spacing)
            resample.SetSize(new_size)
            resample.SetOutputDirection(image.GetDirection())
            resample.SetOutputOrigin(image.GetOrigin())
            new_image = resample.Execute(image)
            sitk.WriteImage(new_image, os.path.join(Output_path,str.replace(savename,'.nii.gz','_resampled.nii.gz')))

    def check_for_nifti_completion(self):
        '''iterate over files and check if files have been converted from dicom to nifti format for all series'''

        need_to_process=[]
        for database in self.databases:
            for patient in os.listdir(os.path.join(self.basePATH,database)):
                    need_to_process += [patient]

            print('total of {} patients to convert to nifti masks'.format(len(set(need_to_process))))
            return set(need_to_process)

    def remove_nifti_files(self,database):
        '''iterate over files and remove emtpy nifti files (if there is an error)'''

        need_to_process=[]
        for patient in os.listdir(os.path.join(self.basePATH,database)):
            print(patient)
            if os.path.exists(os.path.join(self.basePATH, database, patient, 'nifti')):
                shutil.rmtree(os.path.join(self.basePATH, database, patient, 'nifti'))
                print('removing data for patient {}'.format(patient))



if __name__=='__main__':
    c=Dicom2Nifti()
    c.dicom_to_nifti()
