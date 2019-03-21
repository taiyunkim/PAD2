import re


# check if the signalfile is correct format or if there are any signals in the file
def checkSignalFile(signalfile_list):
    for signalfile in signalfile_list:
        # signal_dict = {}
        for line in signalfile:
            if re.search('chr[\dA-Z]+', line.decode('utf-8')):
                chromosome = re.search('^chr[\dA-Z]+', line.decode('utf-8'))
                # start, end of each bp bins, count and RPKM of signals
                pos = re.search('\s+\d+\s+\d+\s+\d+\s+\d+\s*', line.decode('utf-8'))
                # split the start and end into separate variables
                if not chromosome or not pos:
                    # Invalid file format!
                    return False
                # start = re.search('^\s\d+\s', pos.group())
                # end = re.search('\s\d+\s$', pos.group())
                # # remove any whitespaces
                # start = re.sub('\s*', '', start.group(0))
                # end = re.sub('\s*', '', end.group(0))
                # midpoint = int((int(start) + int(end))/2)
                # if chromosome.group(0) not in signal_dict.keys():
                #     signal_dict[chromosome.group(0)] = []
                # signal_dict[chromosome.group(0)].append([int(start), int(end), midpoint])
            else:
                return False
        # if not signal_dict:
        #     # list is empty i.e. there is no signals in file
        #     return False
    return True



# def calculatePearsonCor(f1, f2):
