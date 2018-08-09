#!/usr/bin/env python

import numpy
from gnuradio import gr
import pmt
import prbs_base


class prbs_sink_b(gr.sync_block):
    def __init__(self, which_mode="PRBS15", reset_len=100000):
        gr.sync_block.__init__(self, name="prbs_sink_b",
                               in_sig=[numpy.int8], out_sig=[])

        self.base = prbs_base.prbs_base(which_mode, reset_len)
        self.nbits = 0
        self.nerrs = 0

        self.ber_port_id = pmt.intern("ber")
        self.message_port_register_out(self.ber_port_id)

    def work(self, input_items, output_items):
        inb = input_items[0]
        linb = len(inb)
        gen = self.base.gen_n(linb)

        tags = self.get_tags_in_window(0, 0, linb, pmt.intern("rx_time"))

        if tags:
            tag = tags[-1]
            rx_time = tag.value
            seconds = pmt.to_uint64(pmt.tuple_ref(rx_time, 0))
            fractional_seconds = pmt.to_double(pmt.tuple_ref(rx_time, 1))
            timestamp = seconds + fractional_seconds
            if self.nbits > 0:
                ber = self.nerrs / float(self.nbits)
                #print "NBits: %d \tNErrs: %d \tBER: %.4E, \ttimestamp %f"%(int(self.nbits), int(self.nerrs), ber, timestamp)
                d = pmt.make_dict()
                d = pmt.dict_add(d, pmt.intern('timestamp'), pmt.from_double(timestamp))
                d = pmt.dict_add(d, pmt.intern('ber'), pmt.from_double(ber))
                self.message_port_pub(self.ber_port_id, d)
                self.nerrs = 0
                self.nbits = 0

        self.nerrs += numpy.sum(numpy.bitwise_xor(inb, gen))
        self.nbits += len(inb)
        # if self.nbits > 0:
        #     print "NBits: %d \tNErrs: %d \tBER: %.4E"%(int(self.nbits), int(self.nerrs), self.nerrs/self.nbits)

        return len(inb)
