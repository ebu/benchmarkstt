from benchmarkstt.normalization.logger import ListHandler, DiffLoggingFormatter, normalize_logger
import json
import benchmarkstt.csv as csv
import benchmarkstt.normalization as normalization

factory = normalization.factory


def callback(cls, text: str, *args, return_logs: bool = None, **kwargs):
    """
    :param str text: The text to normalize
    :param bool return_logs: Return normalizer logs
    """
    if return_logs:
        handler = ListHandler()
        handler.setFormatter(DiffLoggingFormatter(dialect='html'))
        normalize_logger.addHandler(handler)

    try:
        result = {
            "text": cls(*args, **kwargs).normalize(text)
        }
        if return_logs:
            logs = handler.flush()
            result['logs'] = []
            for log in logs:
                result['logs'].append(dict(names=log[0], message=log[1]))
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
    finally:
        if return_logs:
            normalize_logger.removeHandler(handler)
