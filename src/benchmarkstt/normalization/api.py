from benchmarkstt.normalization.logger import LogCapturer
import json
import benchmarkstt.csv as csv
import benchmarkstt.normalization as normalization

factory = normalization.factory


def callback(cls, text: str, return_logs: bool = None, *args, **kwargs):
    """
    :param str text: The text to normalize
    :param bool return_logs: Return normalization logs
    """
    try:
        instance = cls(*args, **kwargs)
        if not return_logs:
            return dict(text=instance.normalize(text))

        with LogCapturer(dialect='html', diff_formatter_dialect='dict') as logcap:
            result = dict(text=instance.normalize(text))
            result['logs'] = logcap.logs
            return result
    except csv.CSVParserError as e:
        message = 'on line %d, character %d' % (e.line, e.char)
        message = '\n'.join([e.__doc__, e.message, message])
        data = {
            "message": message,
            "line": e.line,
            "char": e.char,
            "index": e.index,
            "field": "config"
        }
        raise AssertionError(json.dumps(data))
