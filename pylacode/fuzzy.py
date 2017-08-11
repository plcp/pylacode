# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import binascii
import hashlib
import operator
import random
import sys
import time

import pylacode as pl
import pylacode.error
import pylacode.tools
import pylacode.source

assert sys.version_info >= (2, 7)

logic_type = pl.logic.tbsl

_local_occuring_uid = 0

uuid_magic = '49e'
uuid_session = None


def reset_session():
    global uuid_session
    uuid_session = random.uniform(0, 1).hex()[4:10]


reset_session()


def create_uuid(source):
    global _local_occuring_uid

    src = None
    if sys.version_info < (3, ):
        src = str(source).decode('utf8')
    else:
        src = bytes(str(source), 'utf8')

    s = uuid_magic
    s += '-%x%x%02x' % pl.api_version
    s += '-' + uuid_session
    s += '-%08x' % _local_occuring_uid
    s += '-{}'.format(hashlib.sha224(src).hexdigest()[-6:])
    s += '-%08x' % int(time.time())
    s += '-' + random.uniform(0, 1).hex()[4:10]

    src = None
    if sys.version_info < (3, ):
        src = s.decode('utf8')
    else:
        src = bytes(s, 'utf8')

    s += '%08x' % (binascii.crc32(src) & 0xffffffff)
    _local_occuring_uid += 1
    return s


class evidence:
    def __init__(self,
                 value=None,
                 size=None,
                 source=None,
                 merge_operator=operator.add,
                 **mdata):

        if source is None:
            source = pl.source.default
        assert pl.source.issource(source)

        if value is None:
            assert size is not None  # if value is None then size must be given
            self.size = size
            self.value = logic_type(size=self.size)
        else:
            self.value = logic_type(value)
            if size is not None:
                pl.error.warn('Size given but ignored')
            self.size = len(value)

        global _local_occuring_uid
        self.merge_operator = merge_operator
        self.source = source
        self.mdata = dict(**mdata)
        self.uuid = create_uuid(source)
        self.uid = int(_local_occuring_uid)

    def __lshift__(self, other):
        assert isinstance(other, evidence)
        assert len(self.value) == len(other.value)

        value = self.merge_operator(self.value, other.value)
        source = None
        if self.source == other.source:
            source = self.source
        else:
            source = pl.source.merge_source(
                op=self.merge_operator, left=self.source, right=other.source)

        return evidence(
            value=value,
            source=source,
            merge_operator=self.merge_operator,
            **self.mdata)

def squash(*evidences):
    _evidences = []
    for e in evidences:
        _evidences += pl.tools.listify(e)
    evidences = _evidences

    base = evidences[0]
    for e in evidences[1:]:
        base <<= e
    return base
