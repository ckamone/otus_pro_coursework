from optparse import OptionParser


def get_args():
    op = OptionParser()
    op.add_option("-l", "--logfile", action="store", default=None)
    op.add_option("-m", "--mode", action="store", default="stl")
    (opts, args) = op.parse_args()
    return (opts, args)
