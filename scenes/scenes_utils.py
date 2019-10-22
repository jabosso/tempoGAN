import os


class SessionSaver(object):

    def __init__(self, basepath):
        self.base_path = "saved_" + basepath
        self.uni_folder = self.base_path + '/' + 'uni'
        self.screen_folder = self.base_path + '/' + 'screen'
        self.SessionNumber = 0
        self.createCountedFolders()

    def createCountedFolders(self):
        i = 0
        tmp_uni = self.uni_folder + str(i)
        tmp_scr = self.screen_folder + str(i)
        while os.path.exists(tmp_uni) or os.path.exists(tmp_scr):
            i = i + 1
            tmp_uni = self.uni_folder + str(i)
            tmp_scr = self.screen_folder + str(i)
        self.SessionNumber = i
        os.makedirs(tmp_uni)
        self.uni_folder = tmp_uni
        os.makedirs(tmp_scr)
        self.screen_folder = tmp_scr

    def getUniFolder(self):
        return self.uni_folder + '/'

    def getScreenFolder(self):
        return self.screen_folder + '/'
