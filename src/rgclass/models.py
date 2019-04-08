from __future__ import unicode_literals

from django.db import models

# information about peaks in a file
class Signal_db(models.Model):
    """
    The Signal_db class defines the meta-data of the signalfiles in the database.
    **File_ID** - ID of a file.
    **Filename** - Name of the (original) file.
    """
    # fileID = models.IntegerField(db_index=True) # A unique identifier of the file
    fileID = models.CharField(max_length=100)
    filename = models.CharField(db_index=True, max_length=100) # actual original file name
    # proteinName = models.CharField(max_length=) # protein names

    def __unicode__(self):
        return u'%s %s' % (self.fileID, self.filename)

    def __str__(self):
        return '%s %s' % (self.fileID, self.filename)


class Signal_db_info(models.Model):
    """
    The Signal_db_info class defines the normalised coverage of the signalfiles for each regions
    **Region** - Genomic regions
    **FileID** - ID of a file.
    **Value** - normalised coverage
    """
    region = models.CharField(db_index = True, max_length=5)
    value = models.FloatField()
    fileID = models.CharField(db_index=True, max_length=50)

    def __unicode__(self):
        return u'%s %s %f' % (self.region, self.fileID, self.value)

    def __str__(self):
        return '%s %s %f' % (self.region, self.fileID, self.value)
