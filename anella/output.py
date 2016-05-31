class OUTPUT:

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CLOSE = '\033[0m'
    FAIL = '\033[91m'

    @staticmethod
    def info(message, addon=None):
        output = OUTPUT.HEADER + str(message) + OUTPUT.CLOSE
        if addon:
            output += OUTPUT.BLUE + " [" + str(addon) + "]" + OUTPUT.CLOSE
        print output

    @staticmethod
    def error(message):
        print OUTPUT.FAIL + str(message) + OUTPUT.CLOSE
