#!/usr/bin/env python

import numpy
from gnuradio import gr
import prbs_base


class prbs_sink_b(gr.sync_block):
    def __init__(self, which_mode="PRBS15", reset_len=100000):
        gr.sync_block.__init__(self, name="prbs_sink_b",
                               in_sig=[numpy.int8], out_sig=[])

        self.base = prbs_base.prbs_base(which_mode, reset_len)
        self.nbits = 0
        self.nerrs = 0

    def work(self, input_items, output_items):
        inb = input_items[0]
        gen = self.base.gen_n(len(inb))
        self.nerrs += numpy.sum(numpy.bitwise_xor(inb, gen))
        self.nbits += len(inb)

        if self.nbits > 0:
            print "NBits: %d \tNErrs: %d \tBER: %.4E"%(int(self.nbits), int(self.nerrs), self.nerrs/self.nbits)
            #print "NBits: %d \tNErrs: %d \tBER: %g"%(int(self.nbits), int(self.nerrs), self.nerrs/self.nbits)

        return len(inb)
