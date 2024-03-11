#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

"""@brief Interface to pipeline functions.
"""

import os
import sys
from collections import OrderedDict

import runner

maxVarLength = 1000
def setVariable(varName, value):
    # use bash function
    value = str(value)
    if len(value) > maxVarLength:
        print >> sys.stderr, 'Variable is probably too long to work correctly (max %s).' % maxVarLength
        pass
    cmd = "pipelineSet %s '%s'" % (varName, value)
    status = runner.run(cmd)
    return status


def createSubStream(subTask, stream=-1, args=''):
    cmd = "pipelineCreateStream %s %s '%s'" % (subTask, stream, args)
    status = runner.run(cmd)
    return status


def getProcess():
    return os.environ['PIPELINE_PROCESS']


def getStream():
    return os.environ['PIPELINE_STREAM']


def getTask():
    return os.environ['PIPELINE_TASK']


class Pipeline:
    def __init__(self, summary_file=None, process_name=None):
        self.summary_file= os.environ["PIPELINE_SUMMARY"] \
            if summary_file is None else summary_file
        self.process_name = os.environ["PIPELINE_PROCESS"] \
            if process_name is None else process_name
        self._read_summary()

    def _read_summary(self):
        self.data = OrderedDict()
        with open(self.summary_file, 'r') as fobj:
            for line in fobj:
                if not line.strip():
                    continue
                tokens = line.strip().split(':')
                self.data[tokens[0]] = ':'.join(tokens[1:]).strip()

    def getStream(self):
        return int(os.environ['PIPELINE_STREAM'])

    def getProcessInstance(self, process_name):
        summary_file = self.summary_file.replace(self.process_name,
                                                 process_name)
        if not os.path.isfile(summary_file):
            raise RuntimeError("PIPELINE_SUMMARY file not found for %s",
                               summary_file)
        return Pipeline(summary_file=summary_file, process_name=process_name)

    def setVariable(self, key, value):
        with open(self.summary_file, "a") as f:
            full_key = "Pipeline.%s" % key
            f.write("%s: %s\n" % (full_key, value))
        self.data[full_key] = str(value)

    def getVariable(self, key):
        full_key = "Pipeline.%s" % key
        try:
            return self.data[full_key]
        except KeyError:
            return None

    def createSubStream(self, task, stream, args):
        with open(self.summary_file, "a") as f:
            f.write("PipelineCreateStream.%s.%d: %s\n" %
                    (task, int(stream), args))
