#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Dekodowanie UTF-8 dla Python 2, 3
'''

import sys

three_or_more = sys.version >= '3'
et_cdng_eight_utf = 'utf-8'


def konwersja_uni_utf8(napis):
    return napis.encode(et_cdng_eight_utf)
