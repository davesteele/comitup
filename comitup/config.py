
import ConfigParser
import StringIO

class Config(object):
    def __init__(self, filename):
        self.config = ConfigParser.SafeConfigParser()
        conf_str = '[DEFAULT]\n' + open(filename, 'r').read()
        conf_fp = StringIO.StringIO(conf_str)
        self.config.readfp(conf_fp)

    def __getattr__(self, tag):
        try:
            return self.config.get('DEFAULT', tag)
        except:
            pass

        return super(Config, self).__getattr__(tag)

