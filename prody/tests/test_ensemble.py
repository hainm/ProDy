#!/usr/bin/python
# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2011 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module contains unit tests for :mod:`~prody.ensemble` module."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2011 Ahmet Bakan'

import unittest
import numpy as np
from numpy.testing import *

from prody import *
from test_datafiles import *

prody.changeVerbosity('none')

ATOL = 1e-5
RTOL = 0

ATOMS = parseDatafile('multi_model_truncated', subset='ca')
COORDS = ATOMS.getCoordinates()
COORDSETS = ATOMS.getCoordsets()
ENSEMBLE = Ensemble(ATOMS)
CONF = ENSEMBLE[0]
DATA = DATA_FILES['multi_model_truncated']
ENSEMBLE_RMSD = DATA['rmsd_ca']
ENSEMBLE_SUPERPOSE = DATA['rmsd_ca_aligned']

ENSEMBLEW = Ensemble(ATOMS)
ENSEMBLEW.setWeights(np.ones(len(ATOMS), dtype=float))
CONFW = ENSEMBLEW[0]
        
PDBENSEMBLE = PDBEnsemble('PDBEnsemble')
PDBENSEMBLE.setCoordinates(COORDS)
WEIGHTS = []
for i, xyz in enumerate(ATOMS.iterCoordsets()):
    weights = np.ones((len(ATOMS), 1), dtype=float)
    if i > 0:
        weights[i] = 0
        weights[-i] = 0 
        PDBENSEMBLE.addCoordset(xyz, weights=weights)
    else:
        PDBENSEMBLE.addCoordset(xyz)
    WEIGHTS.append(weights)
PDBCONF = PDBENSEMBLE[0]
WEIGHTS = np.array(WEIGHTS)
WEIGHTS_BOOL = np.tile(WEIGHTS.astype(bool), (1,1,3))  
WEIGHTS_BOOL_INVERSE = np.invert(WEIGHTS_BOOL)


class TestEnsemble(unittest.TestCase):
    
    def testGetCoordinates(self):
        """Test correctness of reference coordinates."""
        
        assert_equal(ENSEMBLE.getCoordinates(), COORDS,
                     'failed to get correct coordinates')
    
    
    def testGetCoordsets(self):
        """Test correctness of all coordinates."""

        assert_equal(ATOMS.getCoordsets(), ENSEMBLE.getCoordsets(),
                     'failed to add coordinate sets for Ensemble')
    
    
    def testGetWeights(self):
        """Test correctness of all weights."""

        assert_equal(ENSEMBLEW.getWeights().ndim, 2,
                     'failed to get correct weights ndim')
        assert_equal(ENSEMBLEW.getWeights().shape, 
                     (ENSEMBLEW.numAtoms(), 1),
                    'failed to get correct weights shape')
        assert_equal(ENSEMBLEW.getWeights(),
                     np.ones((ENSEMBLEW.numAtoms(), 1), float),
                     'failed to get expected weights')

    def testSlicingCopy(self):
        """Test making a copy by slicing operation."""
        
        SLICE = ENSEMBLE[:]
        assert_equal(SLICE.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'slicing copy failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), ENSEMBLE.getCoordsets(),
                     'slicing copy failed to add coordinate sets')

    def testSlicing(self):
        """Test slicing operation."""
        
        SLICE = ENSEMBLE[:2]
        assert_equal(SLICE.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'slicing failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), ENSEMBLE.getCoordsets([0,1]),
                     'slicing failed to add coordinate sets')

    def testSlicingList(self):
        """Test slicing with a list."""
        
        SLICE = ENSEMBLE[[0,2]]
        assert_equal(SLICE.getCoordinates(), ENSEMBLE.getCoordinates(),
                     'slicing failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), ENSEMBLE.getCoordsets([0,2]),
                     'slicing failed to add coordinate sets for Ensemble')


    def testSlicingWeights(self):
        """Test slicing operation with weights."""
        
        SLICE = ENSEMBLEW[:2]
        assert_equal(SLICE.getWeights(), ENSEMBLEW.getWeights(),
                     'slicing failed to set weights')

    def testIterCoordsets(self):
        """Test coordinate iteration."""
        
        for i, xyz in enumerate(ENSEMBLE.iterCoordsets()):
            assert_equal(xyz, ATOMS.getCoordsets(i),
                         'failed yield correct coordinates')
            
    def testGetNumAtoms(self):

        self.assertEqual(ENSEMBLE.numAtoms(), ATOMS.numAtoms(),
                         'failed to get correct number of atoms')  
            
    def testGetNumCsets(self):

        self.assertEqual(ENSEMBLE.numCoordsets(), ATOMS.numCoordsets(),
                         'failed to get correct number of coordinate sets')  

    def testGetRMSDs(self):
        
        assert_allclose(ENSEMBLE.getRMSDs(), ENSEMBLE_RMSD,
                        rtol=0, atol=1e-3,  
                        err_msg='failed to calculate RMSDs sets')

    def testSuperpose(self):
        
        ensemble = ENSEMBLE[:]
        ensemble.superpose()
        assert_allclose(ensemble.getRMSDs(), ENSEMBLE_SUPERPOSE,
                        rtol=0, atol=1e-3,
                        err_msg='failed to superpose coordinate sets')

    def testGetRMSDsWeights(self):
        
        assert_allclose(ENSEMBLEW.getRMSDs(), ENSEMBLE_RMSD,
                        rtol=0, atol=1e-3,
                        err_msg='failed to calculate RMSDs')

    def testSuperposeWeights(self):
        
        ensemble = ENSEMBLEW[:]
        ensemble.superpose()
        assert_allclose(ensemble.getRMSDs(), ENSEMBLE_SUPERPOSE,
                        rtol=0, atol=1e-3,
                        err_msg='failed to superpose coordinate sets')

    def testDelCoordsetMiddle(self):
        
        ensemble = ENSEMBLE[:]
        ensemble.delCoordset(1)
        assert_equal(ensemble.getCoordsets(), ATOMS.getCoordsets([0,2]),
                     'failed to delete middle coordinate set for Ensemble')
        
    def testDelCoordsetAll(self):
        
        ensemble = ENSEMBLE[:]
        ensemble.delCoordset(range(len(ENSEMBLE)))
        self.assertIsNone(ensemble.getCoordsets(),
                        'failed to delete all coordinate sets for Ensemble')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'failed when deleting all coordinate sets')


    def testConcatenation(self):
        """Test concatenation of ensembles without weights."""
        
        ensemble = ENSEMBLE + ENSEMBLE
        assert_equal(ensemble.getCoordsets(range(3)), ATOMS.getCoordsets(),
                     'concatenation failed')
        assert_equal(ensemble.getCoordsets(range(3,6)), ATOMS.getCoordsets(),
                     'concatenation failed')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'concatenation failed')

    def testConcatenationWeights(self):
        """Test concatenation of ensembles with weights."""
        
        ensemble = ENSEMBLEW + ENSEMBLEW
        assert_equal(ensemble.getCoordsets(range(3)), ATOMS.getCoordsets(), 
                     'concatenation failed')
        assert_equal(ensemble.getCoordsets(range(3,6)), ATOMS.getCoordsets(),
                     'concatenation failed')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'concatenation failed')
        assert_equal(ensemble.getWeights(), ENSEMBLEW.getWeights(),
                     'concatenation failed')

    def testConcatenationNoweightsWeights(self):
        """Test concatenation of ensembles without and with weights."""
        
        ensemble = ENSEMBLE + ENSEMBLEW
        assert_equal(ensemble.getCoordsets(range(3)), ATOMS.getCoordsets(),
                     'concatenation failed')
        assert_equal(ensemble.getCoordsets(range(3,6)), ATOMS.getCoordsets(),
                    'concatenation failed')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'concatenation failed')
        self.assertIsNone(ensemble.getWeights(), 'concatenation failed')

    def testConcatenationWeightsNoweights(self):
        """Test concatenation of ensembles with and without weights."""
        
        ensemble = ENSEMBLEW + ENSEMBLE 
        assert_equal(ensemble.getCoordsets(range(3)), ATOMS.getCoordsets(),
                     'failed at concatenation for Ensemble')
        assert_equal(ensemble.getCoordsets(range(3,6)), ATOMS.getCoordsets(),
                     'failed at concatenation for Ensemble')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'failed at concatenation for Ensemble')
        assert_equal(ensemble.getWeights(), ENSEMBLEW.getWeights(),
                     'failed at concatenation for Ensemble')


class TestConformation(unittest.TestCase): 
    
    
    def testCoordinates(self):
        
        assert_equal(CONF.getCoordinates(), COORDS,
                     'failed to get coordinates for conformation')
                        
    def testWeights(self):
        
        weights = CONFW.getWeights()
        self.assertEqual(weights.ndim, 2,
                        'wrong ndim for weights of Conformation')
        self.assertTupleEqual(weights.shape, 
                              (CONFW.numAtoms(), 1),
                              'wrong shape for weights of Conformation')
        assert_equal(weights, np.ones((ATOMS.numAtoms(), 1), float),
                     'failed to set weights for Conformation')
                                                
    def testCoordinatesForAll(self):
        
        for i, conf in enumerate(ENSEMBLE):
            assert_equal(conf.getCoordinates(), ATOMS.getCoordsets(i),
                         'failed to get coordinates for Conformation')
                         
    def testGetIndex(self):
        """Test get index function."""

        for i, conf in enumerate(ENSEMBLE):
            self.assertEqual(conf.getIndex(), i,
                             'failed to get correct index')        
                        
    def testGetNumAtoms(self):
        """Test get index function."""

        for i, conf in enumerate(ENSEMBLE):
            self.assertEqual(conf.numAtoms(), ATOMS.numAtoms(),
                             'failed to get correct number of atoms')        

class TestPDBEnsemble(unittest.TestCase):
    
    def testGetCoordinates(self):
        
        assert_equal(PDBENSEMBLE.getCoordinates(), COORDS,
                     'failed to set reference coordinates for PDBEnsemble')
    
    def testGetCoordsets(self):

        assert_equal(PDBENSEMBLE.getCoordsets()[WEIGHTS_BOOL], 
                     ATOMS.getCoordsets()[WEIGHTS_BOOL],
                     'failed to add coordinate sets for PDBEnsemble')
    
    def testGetWeights(self):

        self.assertEqual(PDBENSEMBLE.getWeights().ndim, 3,
                        'wrong ndim for weights of PDBEnsemble')
        self.assertTupleEqual(PDBENSEMBLE.getWeights().shape, 
                              (PDBENSEMBLE.numCoordsets(),
                               PDBENSEMBLE.numAtoms(), 1),
                               'wrong shape for weights of PDBEnsemble')
        assert_equal(PDBENSEMBLE.getWeights(), WEIGHTS,
                     'failed to get correct weights')


    def testSlicingCopy(self):
        
        SLICE = PDBENSEMBLE[:]
        assert_equal(SLICE.getCoordinates(), PDBENSEMBLE.getCoordinates(),
                     'slicing copy failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), PDBENSEMBLE.getCoordsets(),
                     'slicing copy failed to add coordinate sets')

    def testSlicing(self):
        
        SLICE = PDBENSEMBLE[:2]
        assert_equal(SLICE.getCoordinates(), PDBENSEMBLE.getCoordinates(),
                     'slicing failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), PDBENSEMBLE.getCoordsets([0,1]),
                     'slicing failed to add coordinate sets')

    def testSlicingList(self):
        
        SLICE = PDBENSEMBLE[[0,2]]
        assert_equal(SLICE.getCoordinates(), PDBENSEMBLE.getCoordinates(),
                     'slicing failed to set reference coordinates')
        assert_equal(SLICE.getCoordsets(), PDBENSEMBLE.getCoordsets([0,2]),
                     'slicing failed to add coordinate sets')

    def testSlicingWeights(self):
        
        SLICE = PDBENSEMBLE[:2]
        assert_equal(SLICE.getWeights(), PDBENSEMBLE.getWeights()[:2],
                     'slicing failed to set weights')

    def testIterCoordsets(self):
        
        for i, xyz in enumerate(ENSEMBLE.iterCoordsets()):
            assert_equal(xyz[WEIGHTS_BOOL[i]], 
                         ATOMS.getCoordsets(i)[WEIGHTS_BOOL[i]],
                         'failed iterate coordinate sets')
            
    def testGetNumAtoms(self):

        self.assertEqual(PDBENSEMBLE.numAtoms(), ATOMS.numAtoms(),
                         'failed to get correct number of atoms')  
            
    def testGetNumCsets(self):

        self.assertEqual(PDBENSEMBLE.numCoordsets(), 
                         ATOMS.numCoordsets(),
                         'failed to get correct number of coordinate sets')  

    def testDelCoordsetMiddle(self):
        
        ensemble = PDBENSEMBLE[:]
        ensemble.delCoordset(1)
        assert_equal(ensemble.getCoordsets()[WEIGHTS_BOOL[[0,2]]],
                     ATOMS.getCoordsets([0,2])[WEIGHTS_BOOL[[0,2]]], 
                    'failed to delete middle coordinate set')
        
    def testDelCoordsetAll(self):
        """Test consequences of deleting all coordinate sets."""
        
        ensemble = PDBENSEMBLE[:]
        ensemble.delCoordset(range(len(PDBENSEMBLE)))
        self.assertIsNone(ensemble.getCoordsets(),
                        'failed to delete all coordinate sets')
        self.assertIsNone(ensemble.getWeights(), 'failed to delete weights '
                          'with all coordinate sets')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'failed to delete all coordinate sets')


    def testConcatenation(self):
        """Test concatenation of PDB ensembles."""
        
        ensemble = PDBENSEMBLE + PDBENSEMBLE
        assert_equal(ensemble.getCoordsets(range(3)),
                     PDBENSEMBLE.getCoordsets(), 
                     'concatenation failed')
        assert_equal(ensemble.getCoordsets(range(3,6)),
                     PDBENSEMBLE.getCoordsets(), 
                     'concatenation failed')
        assert_equal(ensemble.getCoordinates(), COORDS,
                     'concatenation failed')
        assert_equal(ensemble.getWeights()[range(3)],
                     PDBENSEMBLE.getWeights(),
                     'concatenation failed')
        assert_equal(ensemble.getWeights()[range(3,6)], 
                     PDBENSEMBLE.getWeights(),
                     'concatenation failed')

class TestPDBConformation(unittest.TestCase): 
    
    
    def testCoordinates(self):
        
        assert_equal(PDBCONF.getCoordinates(), COORDS,
                     'failed to get correct coordinates')
                        
    def testWeights(self):
        
        weights = PDBCONF.getWeights()
        self.assertEqual(weights.ndim, 2,
                        'wrong ndim for weights')
        self.assertTupleEqual(weights.shape, (PDBCONF.numAtoms(), 1),
                              'wrong shape for weights')
        assert_equal(PDBCONF.getWeights(), WEIGHTS[0],
                     'failed to set weights')

    def testWeightsForAll(self):

        for i, conf in enumerate(PDBENSEMBLE):
            assert_equal(conf.getWeights(), WEIGHTS[i],
                         'failed to set weights')

                                                
    def testCoordinatesForAll(self):
        
        for i, conf in enumerate(PDBENSEMBLE):
            assert_equal(conf.getCoordinates()[WEIGHTS_BOOL[i]], 
                         ATOMS.getCoordsets(i)[WEIGHTS_BOOL[i]],
                         'failed to get coordinates')
                         
    def testGetIndex(self):

        for i, conf in enumerate(PDBENSEMBLE):
            self.assertEqual(conf.getIndex(), i,
                             'failed to get correct index')        
                        
    def testGetNumAtoms(self):

        for i, conf in enumerate(PDBENSEMBLE):
            self.assertEqual(conf.numAtoms(), ATOMS.numAtoms(),
                             'failed to get correct number of atoms')

class TestCalcSumOfWeights(unittest.TestCase):

    def testResults(self):
        assert_equal(calcSumOfWeights(PDBENSEMBLE), WEIGHTS.sum(0).flatten(),
                     'calcSumOfWeights failed')

    def testInvalidType(self):
        
        self.assertRaises(TypeError, calcSumOfWeights, ENSEMBLE)
        
    def testWeightsNone(self):
        
        self.assertIsNone(calcSumOfWeights(PDBEnsemble()),
                          'calcSumOfWeights failed')


if __name__ == '__main__':
    prody.changeVerbosity('none')
    unittest.main()
    prody.changeVerbosity('debug')