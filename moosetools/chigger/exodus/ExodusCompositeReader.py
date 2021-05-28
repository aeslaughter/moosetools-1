import glob
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from moosetools import mooseutils
from .ExodusReader import ExodusReader
from .. import base

class ExodusCompositeReader(base.ChiggerAlgorithm, VTKPythonAlgorithmBase):

    """
    A reader for handling multiple ExodusII files.

    This class is simply a wrapper that creates and ExodusReader object for each file found using
    glob from the supplied pattern.
    """
    @staticmethod
    def validParams():
        opt = ExodusReader.validParams()
        opt.remove('filename')
        opt.add('pattern', vtype=str, required=True, mutable=False,
                doc="The filename pattern to use for loading multiple ExodusII files.")
        return opt

    def __init__(self, **kwargs):
        ExodusReader.__CHIGGER_CURRENT__ = self
        base.ChiggerAlgorithm.__init__(self, **kwargs)
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=0,
                                        inputType='vtkMultiBlockDataSet',
                                        outputType='vtkMultiBlockDataSet')

        self.__readers = list()
        filenames = sorted(glob.glob(self.getParam('pattern')))
        self.SetNumberOfInputPorts(len(filenames))

        for index, filename in enumerate(filenames):
            params = ExodusReader.validParams()
            params.setValue('filename', filename)
            params.update(self.parameters())
            self.__readers.append(ExodusReader(**params.toDict()))
            self.SetInputConnection(index, self.__readers[-1].GetOutputPort(0))

    def _onRequestData(self, inInfo, outInfo):
        """(override, protected)
        Do not call this method, call updateData.
        """
        base.ChiggerAlgorithm._onRequestData(self, inInfo, outInfo)

        blocks = vtk.vtkMultiBlockDataSet()
        for index in range(len(inInfo)):
            inp = inInfo[index].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
            blocks.SetBlock(index, inp)
        blocks.Update()

        extract = vtk.vtkExtractBlock()
        extract.AddIndex(0)
        extract.SetInputData(blocks)
        extract.Update()

        out_data = outInfo.GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        out_data.ShallowCopy(extract.GetOutputDataObject(0))

    def __iter__(self):
        """
        Provide iterator access to the readers.
        """
        for reader in self.__readers:
            yield reader

    def __getitem__(self, index):
        """
        Provide operator[] access to the readers.
        """
        return self.__readers[index]

    def __str__(self):
        """
        Return the ExodusReader information for each file.
        """
        out = ''
        for reader in self.__readers:
            out += '\n\n' + mooseutils.colorText(reader.filename(), 'MAGENTA')
            out += str(reader)
        return out

    def setParam(self, *args, **kwargs):
        """
        Set single option for all contained readers.
        """
        super(CompositeAppExodusReader, self).setParam(*args, **kwargs)
        for reader in self.__readers:
            reader.setParam(*args, **kwargs)

    def setParams(self, *args, **kwargs):
        """
        Set options for all contained readers.
        """
        super(CompositeAppExodusReader, self).setParams(*args, **kwargs)
        for reader in self.__readers:
            reader.setParams(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Update all readers.
        """
        super(CompositeAppExodusReader, self).update(*args, **kwargs)
        for reader in self.__readers:
            reader.update(*args, **kwargs)