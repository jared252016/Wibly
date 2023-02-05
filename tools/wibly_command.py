from tools.wibly_tools import md5_hash_text
import os
import tools.wibly_logging
class wibly_command:
    CONFIG = None
    name = None
    crawler = None
    action = None
    cache = None
    dl_location = None
    critera = None
    total_downloaded = 0
    args = {}
    LOGGER = None
    def __init__(self, crawler, name, config):
        self.LOGGER = tools.wibly_logging.getLogger()
        self.crawler = crawler
        self.name = name
        self.CONFIG = config
        self.action = self.CONFIG["action"]
        if "cache" in self.CONFIG:
            self.cache = self.CONFIG["cache"]
        if "location" in self.CONFIG:
            self.dl_location = self.CONFIG["location"]
        if "args" in self.CONFIG:
            self.parse_args()

    def has_args(self, name):
        if name in self.args:
            return True
        else:
            return False

    def parse_args(self):
        for arg in self.CONFIG['args']:
            for key,val in arg.items():
                self.args[key] = val

    def parse_critera(self, item):
        temp = {}
        critera = self.CONFIG['critera']
        for key,val in critera.items():
            if "detector" in val:
                if self.crawler.has_property_item_name(item, val["detector"]):
                    temp[key] = val
        self.critera = temp
        
    def run(self, item):
        if "critera" in self.CONFIG:
            self.parse_critera(item)
        if self.action == "youtube-dl":
            self.LOGGER.info("Running action: youtube-dl")
            if self.critera_met(item):
                self.download_with_youtubedl(item)

    def critera_met(self, item):
        success = False
        for key,critera in self.critera.items():
            self.LOGGER.debug("[Critera][%s] %s" % (key, str(critera)))
            detector = critera["detector"]
            if "mode" in critera:
                mode = critera["mode"]
            else:
                mode = "single"
            if "modify" in critera:
                modify = critera["modify"]
            else:
                modify = False
            if self.crawler.has_property_item_name(item, detector):
                param = self.crawler.get_property_item_value(item, detector)
                require = critera["require"]
                if modify == "upper":
                    for r in require:
                        r = r.upper()
                elif modify == "lower":
                    for r in require:
                        r = r.lower()
                if mode == "single":
                    require = require[0]
                    if require in param: # We need to turn detector.title into the title
                        success = True
                elif mode == "or":
                    for required_item in require:
                        if required_item in param:
                            success = True
                else: # Assume 'and'
                    success_cnt = 0
                    total_cnt = len(require)
                    for required_item in require:
                        if required_item in param:
                            success_cnt += 1
                    if success_cnt == total_cnt:
                        success = True
            else:
                self.LOGGER.debug("[Critera][Success] False")
                return False
        self.LOGGER.debug("[Critera][Success] %s" % (str(success),))
        return success

    def download_with_youtubedl(self, item):
        if self.cache == None:
            self.cache = "cache/"
        if not os.path.exists(self.cache):
            os.mkdir(self.cache)

        if self.has_args("no_check_certificate"):
            no_check_certificate = "--no-check-certificate"
        else:
            no_check_certificate = ""
        
        href = self.crawler.get_property_item_value(item, "video_url")
        cache_file = os.path.join(self.cache, md5_hash_text(self.dl_location) + ".txt")
        out_file = os.path.join(self.dl_location, '%(title)s-%(id)s.%(ext)s')
        self.LOGGER.info("["+str(self.total_downloaded)+"/??][DOWNLOAD][YOUTUBE-DL][wibly_auto] " + href + " - archive: " + cache_file + " - Saving To: " + out_file)
        returncode = os.system('youtube-dl --download-archive "'+cache_file+'" --external-downloader aria2c --external-downloader-args "-x 16 -s 16 -k 1M" '+no_check_certificate+' -o "'+ out_file + '" ' + str(href))
        self.LOGGER.info("["+str(self.total_downloaded)+"/??][DOWNLOAD][YOUTUBE-DL] Returned " + str(returncode))
        self.total_downloaded += 1
        