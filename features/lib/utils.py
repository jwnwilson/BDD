# -*- coding: utf-8 -*-
import pdb
import sys


def set_trace():
    """Crude way to add breakpoint to tests for debugging
    """
    pdb.Pdb(stdout=sys.__stdout__).set_trace()
