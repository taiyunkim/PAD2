import re
import os

from django.conf import settings

# import pybedtools as pb
from multiprocessing import Pool
import subprocess




# check if the signalfile is correct format or if there are any signals in the file
def checkSignalFile(signalfile_list):
    for signalfile in signalfile_list:
        # signal_dict = {}
        for line in signalfile:
            if re.search('chr[\dA-Za-z]+', line.decode('utf-8')):
                chromosome_pos = re.search('^chr[\dA-Za-z\_]+\_[0-9]+', line.decode('utf-8'))
                # start, end of each bp bins, count and RPKM of signals
                # pos = re.search('\s+\d+\s+\d+\s+\d+\s+\d+\s*', line.decode('utf-8'))
                val = re.search('\s+\d+\s[\d\.]+\s*.*$', line.decode('utf-8'))

                # split the start and end into separate variables
                if not chromosome_pos or not val:
                    # Invalid file format!
                    return False

            else:
                return False
    return True


# Unlike the function in tfclass, this is also to split the file to region
def createPeakToBedFile(peakfile_list, session_id):
    for peakfile in peakfile_list:
        filepath = peakfile.file.name
        filename = peakfile.name

        path = os.path.join(settings.MEDIA_ROOT, 'PAD2', 'users_signal_files', session_id)
        # calculate gene dist and return as a dict
        
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, '')
    
        script_path = os.path.join(settings.MEDIA_ROOT, 'scripts', 'processSignals_2_user.sh')
        # peak_dict = separateSignal(peak_dict, db_name)

        subprocess.run(['bash', script_path, path, filepath, filename])
        # write to a bedfile with gene_dist so that in the future when user dynamically ask for different cutoff, it can use
        # other function to create another file
        # store to the db Peaks_db_file with cutoff as 0 and with given path and then return
        # createUserPeakBed(peak_dict, filename, db_name, path)
    return True





# def processFun(path, filename):
#     a = pb.BedTool(os.path.join(path, filename))
#     # head_name = re.sub("(.*)(\.bed)", "\\1", i)
#     a.intersect(b, wa = True).saveas(os.path.join(output, filename))



# def separateSignal(peak_dict, db_name):
#     chromosome_set = peak_dict.keys()
#     # index for peaks_list

#     refFilepath = os.path.join(settings.MEDIA_ROOT, '')
#     onlyRefs = [f for f in os.listdir(refFilepath) if os.path.isfile(os.path.join(refFilepath, f))]
#     onlyRefs = [f for f in onlyRefs if '.DS_Store' not in f]

#     indices = [j for j, s in enumerate(onlyRefs) if i in s]

#     b = pb.BedTool(os.path.join(refFilepath, onlyRefs[indices[0]]))
#     # if not os.path.exists(os.path.join(output, 'new', ('subset'+ str(i)))):
#     #     os.makedirs(os.path.join(output, 'new', ('subset'+ str(i))))
#     pool = Pool(int(cores))
#     pool.map(processFun, onlyfiles)
#     pb.cleanup()


