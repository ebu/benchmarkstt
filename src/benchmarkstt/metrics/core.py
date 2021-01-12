from benchmarkstt.schema import Schema
import logging
from collections import namedtuple
from typing import Union
from benchmarkstt.diff import DifferInterface, factory as differ_factory
from benchmarkstt.diff.core import RatcliffObershelp, Levenshtein
from benchmarkstt.diff.formatter import format_diff
from benchmarkstt.metrics import Metric
from collections import namedtuple
import editdistance

logger = logging.getLogger(__name__)

OpcodeCounts = namedtuple('OpcodeCounts',
                          ('equal', 'replace', 'insert', 'delete'))

type_schema = Union[Schema, list]
type_differ = DifferInterface


def traversible(schema, key=None):
    if key is None:
        key = 'item'
    return [item if type(item) is str else item[key] for item in schema]


def get_differ(a, b, differ_class: type_differ):
    if differ_class is None or differ_class == '':
        differ_class = RatcliffObershelp
    elif type(differ_class) is str:
        differ_class = differ_factory[differ_class]
    return differ_class(traversible(a), traversible(b))


class WordDiffs(Metric):
    """
    Present differences on a per-word basis

    :param differ_class: see :py:mod:`benchmarkstt.diff.core`
    :param dialect: Presentation format. Default is 'ansi'.
    :example differ_class: 'levenshtein'
    :example dialect: 'html'
    """

    def __init__(self, differ_class: type_differ = None, dialect: str = None):
        self._differ_class = differ_class
        self._dialect = dialect

    def compare(self, ref: type_schema, hyp: type_schema):
        differ = get_differ(ref, hyp, differ_class=self._differ_class)
        a = traversible(ref)
        b = traversible(hyp)
        return format_diff(a, b, differ.get_opcodes(),
                           dialect=self._dialect,
                           preprocessor=lambda x: ' %s' % (' '.join(x),))


class WER(Metric):
    """
    Word Error Rate, basically defined as::

        insertions + deletions + substitions
        ------------------------------------
             number of reference words

    See: https://en.wikipedia.org/wiki/Word_error_rate

    Calculates the WER using one of two algorithms:

    [Mode: 'strict' or 'hunt'] Insertions, deletions and
    substitutions are identified using the Hunt–McIlroy
    diff algorithm. The 'hunt' mode applies 0.5 weight to
    insertions and deletions. This algorithm is the one
    used internally by Python.

    See https://docs.python.org/3/library/difflib.html

    :param mode: 'strict' (default), 'hunt' or 'levenshtein'.
    :param differ_class: see :py:mod:`benchmarkstt.diff.core`
    """

    # WER modes
    MODE_STRICT = 'strict'
    MODE_HUNT = 'hunt'

    DEL_PENALTY = 1
    INS_PENALTY = 1
    SUB_PENALTY = 1

    def __init__(self, mode=None, differ_class: Union[str, type_differ, None] = None):
        self._mode = mode

        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class

        if mode == self.MODE_HUNT:
            self.DEL_PENALTY = self.INS_PENALTY = .5

    def compare(self, ref: type_schema, hyp: type_schema) -> float:
        diffs = get_differ(ref, hyp, differ_class=self._differ_class)

        try:
            counts = diffs.get_opcode_counts()

            changes = counts.replace * self.SUB_PENALTY + \
                counts.delete * self.DEL_PENALTY + \
                counts.insert * self.INS_PENALTY

            total = counts.equal + counts.replace + counts.delete
            if total == 0:
                return 1 if changes else 0
            return changes / total
        except NotImplementedError:
            return diffs.get_error_rate()


class CER(Metric):
    """
    Character Error Rate, basically defined as::

        insertions + deletions + substitutions
        --------------------------------------
            number of reference characters

    Character error rate, CER, compare the differences
    between reference and hypothesis on a character level.
    A CER measure is usually lower than WER measure, since
    words might differ on only one or a few characters, and
    be classified as fully different.

    The CER metric might be useful as a perspective on the
    WER metric. Word endings might be less relevant if the
    text will be preprocessed with stemming, or minor
    spelling mistakes might be acceptable in certain
    situations. A CER metric might also be used to evaluate
    a source (an ASR) which output a stream of characters
    rather than words.

    Important: The current implementation of the CER metric
    ignores whitespace characters. A string like 'aa bb cc'
    will first be split into words, ['aa','bb','cc'], and
    then merged into a final string for evaluation: 'aabbcc'.

    :param differ_class: see :py:mod:`benchmarkstt.diff.core`
    """

    def __init__(self, differ_class: Union[str, type_differ, None] = None):
        self._differ_class = Levenshtein if differ_class is None else differ_class

    def compare(self, ref: type_schema, hyp: type_schema):
        ref_str = ''.join(traversible(ref))
        hyp_str = ''.join(traversible(hyp))

        if len(ref_str) == 0:
            return 0 if len(hyp_str) == 0 else 1

        diffs = get_differ(ref_str, hyp_str, differ_class=self._differ_class)
        return diffs.get_error_rate()


class DiffCounts(Metric):
    """
    Get the amount of differences between reference and hypothesis

    :param differ_class: see :py:mod:`benchmarkstt.diff.core`
    """

    def __init__(self, differ_class: Union[str, type_differ, None] = None):
        self._differ_class = differ_class

    def compare(self, ref: type_schema, hyp: type_schema) -> OpcodeCounts:
        diffs = get_differ(ref, hyp, differ_class=self._differ_class)
        return diffs.get_opcode_counts()


class BEER(Metric):
    """
    Bag of Entities Error Rate, BEER, is defined as the error rate per entity with a bag of words approach::

                            abs(ne_hyp - ne_ref)
        BEER (entity)   =   ----------------------
                                ne_ref

    - ne_hyp = number of detections of the entity in the hypothesis file
    - ne_ref = number of detections of the entity in the reference file

    The WA_BEER for a set of N entities is defined as the weighted average of the BEER for the set of
    entities::

        WA_BEER ([entity_1, ... entity_N) =  w_1*BEER (entity_1)*L_1/L + ... + w_N*BEER (entity_N))*L_N/L

    which is equivalent to::

                                            w_1*abs(ne_hyp_1 - ne_ref_1) + ... + w_N*abs(ne_hyp_N - ne_ref_N)
        WA_BEER ([entity_1, ... entity_N) = ------------------------------------------------------------------
                                                                            L

    - L_1 =  number of occurrences of entity 1 in the reference document
    - L = L_1 + ... + L_N

    the weights being normalised by the tool:

    - w_1 + ... + w_N = 1

    The input file defines the list of entities and the weight per entity, w_n. It is processed as a json file with the
    following structure::

        { "entity_1":W_1, "entity_2" : W_2, "entity_3" :W_3 .. }

    W_n being the non-normalized weight, the normalization of the weights is performed by the tool as::

                    W_n
        w_n =   ---------------
                W_1 + ... +W_N

    The minimum value for weight being 0.

    """

    def __init__(self, entities_file=None):
        """
        """
        self._error_message = None
        self._entities = None

        if entities_file is not None:
            try:
                with open(entities_file) as f:
                    data = json.load(f)
                    self._entities = list(data.keys())
                    weight = list(data.values())
                    self.set_weight(weight)
            except (IOError, json.decoder.JSONDecodeError) as e:
                self._error_message = str(e)
        return

    def get_weight(self):
        return self._weight

    def set_weight(self, weight):
        weight = [0 if w < 0 else w for w in weight]
        sw = sum(weight)
        if sw > 0:
            self._weight = [w / sw for w in weight]
        # if the sum of the weights is null, the wa_beer is null
        else:
            self._weight = weight

    def get_entities(self):
        return self._entities

    def set_entities(self, entities):
        self._entities = entities

    # find the position of one entity
    # an entity can contain more than one word
    @staticmethod
    def __find_pattern(search_list, complex_entity):
        entity = ''.join(complex_entity).split(' ')
        le = len(entity)
        # complex_entity = [entity1 entity2 ...]
        # the cursor sweep complex_entity to find consecutive entities entity1 ... entity2
        cursor = 0
        idx_found = []
        for idx_sl, elt in enumerate(search_list):
            if elt == entity[cursor]:
                cursor += 1
                if cursor == le:
                    idx_found.append(list(range(idx_sl - le + 1, idx_sl - le + 1 + le)))
                    cursor = 0
            else:
                cursor = 0
        return idx_found

    # generate a list containing the detected entities in list_parsed
    def __generate_list_entity(self, list_parsed):

        list_entity = []
        index_entities = []
        entities = self._entities
        for entity in entities:
            index_entity = self.__find_pattern(list_parsed, entity)
            index_entities.extend(index_entity)

        # sort on the position of the first part of the entity
        index_entities.sort(key=lambda l: l[0])

        # copy-past the entity found in the list
        for k_list in index_entities:
            list_entity.append(' '.join(list_parsed[k_list[0]:k_list[-1] + 1]))

        return list_entity

    # computes the BEER
    def compute_beer(self, list_hypothesis_entity, list_reference_entity):
        beer = {}
        beer_av = 0
        entities = self._entities
        for idx, entity in enumerate(entities):
            count_hypothesis = list_hypothesis_entity.count(entity)
            count_ref = list_reference_entity.count(entity)
            beer_entity = 0
            if count_ref != 0:
                beer_entity = round(abs(count_ref - count_hypothesis) / count_ref, 3)
                # accumulate the distance per entity
                beer_av += abs(count_ref - count_hypothesis) * self._weight[idx]
            beer[entity] = {'beer': beer_entity, 'occurrence_ref': count_ref}

        l_ref = len(list_reference_entity)
        if l_ref > 0:
            beer_av = round(beer_av / l_ref, 3)
        else:
            beer_av = 0
        beer['w_av_beer'] = {'beer': beer_av, 'occurrence_ref': l_ref}
        return beer

    def compare(self, ref: Schema, hyp: Schema):

        if self._entities is None:
            if self._error_message:
                return {'Error': self._error_message}
            else:
                return {'Error': 'Missing .json input file'}

        # get the list of reference and hypothesis
        ref_list = [i['item'] for i in ref]
        hyp_list = [i['item'] for i in hyp]

        # extract the entities
        list_hypothesis_entity = self.__generate_list_entity(hyp_list)
        list_reference_entity = self.__generate_list_entity(ref_list)
        # compute the score
        wer_entity = self.compute_beer(list_hypothesis_entity, list_reference_entity)

        return wer_entity

# For a future version
# class ExternalMetric(LoadObjectProxy, Base):
#     """
#     Automatically loads an external metric class.
#
#     :param name: The name of the metric to load (eg. mymodule.metrics.MyOwnMetricClass)
#     """
