"""Compute Sentiment with SentiWS and vaderSentiment."""
import os
import re
import math
import string
from itertools import product
from inspect import getsourcefile
from io import open
import spacy
# ##Constants##

# (empirically derived mean sentiment intensity rating increase for booster
#  words) (by sentiment_vader for the corresponding english words)
B_INCR = 0.293
B_DECR = -0.293

# (empirically derived mean sentiment intensity rating increase for using
#  ALLCAPs to emphasize a word) (by sentiment_vader for english words)
C_INCR = 0.733
N_SCALAR = -0.74
nlp = spacy.load("de_core_news_sm", disable=["ner", "textcat"])

# for removing punctuation
REGEX_REMOVE_PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))

PUNC_LIST = [".", "!", "?", ",", ";", ":", "-", "'", "\"",
             "!!", "!!!", "??", "???", "?!?", "!?!", "?!?!", "!?!?"]
NEGATE = \
    ["nicht", "kein", "keine", "noch", "nie", "niemals", "weder", "keinem",
     "keiner", "keines", "keinen", "nichts", "nirgends", "nirgendwo", "selten",
     "obwohl", "obgleich", "ausnahmsweise"]

# booster/dampener 'intensifiers' or 'degree adverbs'
# http://en.wiktionary.org/wiki/Category:English_degree_adverbs

BOOSTER_DICT = \
    {"absolut": B_INCR, "unglaublich": B_INCR, "furchtbar": B_INCR,
     "komplett": B_INCR, "considerably": B_INCR, "entschieden": B_INCR,
     "zutiefst": B_INCR, "verdammt": B_INCR, "enorm": B_INCR,
     "völlig": B_INCR, "gänzlich": B_INCR, "vollkommen": B_INCR,
     "ganz": B_INCR, "besonders": B_INCR, "außergewähnlich": B_INCR,
     "ungewöhnlich": B_INCR, "außerodentlich": B_INCR, "äußerst": B_INCR,
     "extrem": B_INCR, "verdammt": B_INCR, "bedeutend": B_INCR,
     "außerodentlich": B_INCR, "sehr": B_INCR, "ungeheur": B_INCR,
     "intensiv": B_INCR, "wahnsinnig": B_INCR, "mehr": B_INCR,
     "meisten": B_INCR, "insbesondere": B_INCR, "vollständig": B_INCR,
     "wirklich": B_INCR, "bemerkenswert": B_INCR, "so": B_INCR,
     "wesentlich": B_INCR, "vollständig": B_INCR, "uneingeschränkt": B_INCR,
     "total": B_INCR, "ungemein": B_INCR, "gründlich": B_INCR, "sogar": B_INCR,
     "entsetzlich": B_INCR, "unnormal": B_INCR, "schlichtweg": B_INCR,
     "fast": B_DECR, "beinahe": B_DECR, "nahezu": B_DECR, "kaum": B_DECR,
     "gerade": B_DECR,  "schwerlich": B_DECR, "gerade genug": B_DECR,
     "irgendwie": B_DECR, "wenig": B_DECR, "gering": B_DECR,
     "bisschen": B_DECR, "marginal": B_DECR, "geringfügig": B_DECR,
     "unwesentlich": B_DECR, "zeitweise": B_DECR, "gelegentlich": B_DECR,
     "mitunter": B_DECR, "teilweise": B_DECR, "spärlich": B_DECR,
     "schwach": B_DECR, "entfernt": B_DECR, "einigermaßen": B_DECR,
     "sozusagen": B_DECR}


def negated(input_words):
    """Determine if input contains negation words.

    Arguments:
    input_words -- input

    Returns:
    neg_words_in_input -- True if there are negated words in input_words

    """
    neg_words_in_input = False
    # will be True if there are negated words in input_words
    input_words = [str(w).lower() for w in input_words]
    # make words lowercase
    neg_words = []
    neg_words.extend(NEGATE)
    # copy words of NEGATE-list into neg_words
    for word in neg_words:
        # check if there are negated words in input_words
        if word in input_words:
            neg_words_in_input = True
    return neg_words_in_input


def normalize(score, alpha=15):
    """Normalize the score to be between -1 and 1self.

    Arguments:
    score -- score to normalize
    alpha -- factor for normalization

    Returns:
    norm_score -- normalized scores

    """
    norm_score = score / math.sqrt((score * score) + alpha)
    if norm_score < -1.0:
        norm_score = -1.0
    elif norm_score > 1.0:
        norm_score = 1.0
    return norm_score


def scalar_inc_dec(word, valence):
    """Check if the preceding words increase, decrease, or negate the valence.

    Arguments:
    word -- check if this word increases/decreases/negates the valence
    valence -- valence-value
    """
    scalar = 0.0
    word_lower = word.lower()
    if word_lower in BOOSTER_DICT:
        scalar = BOOSTER_DICT[word_lower]
        if valence < 0:
            scalar *= -1
    # get the scalar-value of the dict and negate it if needed
    return scalar


class SentiText(object):
    """Identify sentiment-relevant string-level properties of input text.

    Arguments:
    object -- text that should be analyzed
    """

    def __init__(self, text):
        """Initialize SentiText.

        Arguments:
        text -- text that should be analyzed

        """
        if not isinstance(text, str):
            text = str(text).encode('utf-8')
        self.text = text
        self.words_and_emoticons = self._words_and_emoticons()
        # doesn't separate words from\
        # adjacent punctuation (keeps emoticons & contractions)

    def _words_plus_punc(self):
        """Return a dict for removing puctuation.

        Returns:
        words_punc_dict -- mapping of form:
                            {
                                'cat,': 'cat',
                                ',cat': 'cat',
                            }

        """
        no_punc_text = REGEX_REMOVE_PUNCTUATION.sub('', self.text)
        # removes punctuation (but loses emoticons & contractions)
        words_only = no_punc_text.split()
        # remove singletons
        words_only = set(w for w in words_only if len(w) > 1)
        # the product gives ('cat', ',') and (',', 'cat')
        punc_before = {''.join(p): p[1] for p in
                       product(PUNC_LIST, words_only)}
        punc_after = {''.join(p): p[0] for p in product(words_only, PUNC_LIST)}
        words_punc_dict = punc_before
        words_punc_dict.update(punc_after)
        return words_punc_dict

    def _words_and_emoticons(self):
        """Remove puncutation, leave contractions and emoticons.

        Does not preserve punc-plus-letter emoticons (e.g. :D)
        Returns:
        wes -- text without punctuation

        """
        wes = self.text.split()
        words_punc_dict = self._words_plus_punc()
        wes = [we for we in wes if len(we) > 1]
        for i, we in enumerate(wes):
            if we in words_punc_dict:
                wes[i] = words_punc_dict[we]
        return wes


class SentimentIntensityAnalyzer(object):
    """Give a sentiment intensity score to sentences.

    Arguments:
    object -- text to analyze

    """

    def __init__(self, lexicon_file="SentiWS_v2.0_complete_rewritten.txt",
                 emoji_lexicon="emoji_utf8_lexicon.txt"):
        """Initialize everything."""
        _this_module_file_path_ = os.path.abspath(getsourcefile(lambda: 0))
        lexicon_full_filepath = os.path.join(os.path.dirname(
            _this_module_file_path_), lexicon_file)
        with open(lexicon_full_filepath, encoding='utf-8') as f:
            self.lexicon_full_filepath = f.read()
        self.lexicon = self.make_lex_dict()

        emoji_full_filepath = os.path.join(os.path.dirname(
            _this_module_file_path_), emoji_lexicon)
        with open(emoji_full_filepath, encoding='utf-8') as f:
            self.emoji_full_filepath = f.read()
        self.emojis = self.make_emoji_dict()

    def make_lex_dict(self):
        """Convert lexicon file to a dictionary."""
        lex_dict = {}
        for line in self.lexicon_full_filepath.split('\n'):
            if len(line) > 1:
                (word, measure) = line.strip().split('\t')[0:2]
                lex_dict[word] = float(measure)
        return lex_dict

    def make_emoji_dict(self):
        """Convert emoji lexicon file to a dictionary."""
        emoji_dict = {}
        for line in self.emoji_full_filepath.split('\n'):
            (emoji, description) = line.strip().split('\t')[0:2]
            emoji_dict[emoji] = description
        return emoji_dict

    def polarity_scores(self, text):
        """Return a float for sentiment strength based on the input text.

        Positive values are positive valence, negative value are negative
        valence.

        """
        # convert emojis to their textual descriptions
        text_token_list = text.split()
        text_no_emoji_lst = []
        for token in text_token_list:
            if token in self.emojis:
                # get the textual description
                description = self.emojis[token]
                text_no_emoji_lst.append(description)
            else:
                text_no_emoji_lst.append(token)
        text = " ".join(x for x in text_no_emoji_lst)

        sentitext = SentiText(text)

        sentiments = []
        words_and_emoticons = sentitext.words_and_emoticons
        for item in words_and_emoticons:
            valence = 0
            i = words_and_emoticons.index(item)
            # check for vader_lexicon words that may be used as modifiers or
            # negations
            if item.lower() in BOOSTER_DICT:
                sentiments.append(valence)
                continue

            sentiments = self.sentiment_valence(valence, sentitext, item, i,
                                                sentiments)

        sentiments = self._but_check(words_and_emoticons, sentiments)

        valence_dict = self.score_valence(sentiments, text)

        return valence_dict

    def sentiment_valence(self, valence, sentitext, item, i, sentiments):
        """."""
        words_and_emoticons = sentitext.words_and_emoticons
        item_lowercase = item.lower()
        # if item_lowercase not in self.lexicon:
        #     spacy_sent = nlp(sentitext.text)
        #     item_lowercase_stem = spacy_sent[i].lemma_
        #     if item_lowercase_stem in self.lexicon:
        #         item_lowercase = item_lowercase_stem
        if item_lowercase in self.lexicon:
            # get the sentiment valence
            valence = self.lexicon[item_lowercase]
            for start_i in range(0, 3):
                # dampen the scalar modifier of preceding words and emoticons
                # (excluding the ones that immediately preceed the item) based
                # on their distance from the current item.
                if i > start_i and words_and_emoticons[i - (start_i + 1)]\
                        .lower() not in self.lexicon:
                    s = scalar_inc_dec(words_and_emoticons[i - (start_i + 1)],
                                       valence)
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    valence = valence + s
                    valence = self._negation_check(valence,
                                                   words_and_emoticons,
                                                   start_i, i)

        sentiments.append(valence)
        return sentiments

    @staticmethod
    def _but_check(words_and_emoticons, sentiments):
        # check for modification in sentiment due to contrastive conjunction
        words_and_emoticons_lower = [str(w).lower() for
                                     w in words_and_emoticons]
        if 'aber' in words_and_emoticons_lower:
            bi = words_and_emoticons_lower.index('aber')
            for sentiment in sentiments:
                si = sentiments.index(sentiment)
                if si < bi:
                    sentiments.pop(si)
                    sentiments.insert(si, sentiment * 0.5)
                elif si > bi:
                    sentiments.pop(si)
                    sentiments.insert(si, sentiment * 1.5)
        return sentiments

    @staticmethod
    def _negation_check(valence, words_and_emoticons, start_i, i):
        words_and_emoticons_lower = [str(w).lower() for
                                     w in words_and_emoticons]
        if start_i == 0:
            # 1 word preceding lexicon word (w/o stopwords)
            if negated([words_and_emoticons_lower[i - (start_i + 1)]]):
                valence = valence * N_SCALAR
        if start_i == 1:
            if words_and_emoticons_lower[i - 2] == "nie":
                valence = valence * 1.25
            elif words_and_emoticons_lower[i - 2] == "ohne" and \
                    words_and_emoticons_lower[i - 1] == "Zweifel":
                valence = valence
            # 2 words preceding the lexicon word position
            elif negated([words_and_emoticons_lower[i - (start_i + 1)]]):
                valence = valence * N_SCALAR
        if start_i == 2:
            if words_and_emoticons_lower[i - 3] == "ohne" and \
                    (words_and_emoticons_lower[i - 2] == "Zweifel"
                     or words_and_emoticons_lower[i - 1] == "Zweifel"):
                valence = valence
            # 3 words preceding the lexicon word position
            elif negated([words_and_emoticons_lower[i - (start_i + 1)]]):
                valence = valence * N_SCALAR
        return valence

    def _punctuation_emphasis(self, text):
        # add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        punct_emph_amplifier = ep_amplifier + qm_amplifier
        return punct_emph_amplifier

    @staticmethod
    def _amplify_ep(text):
        # check for added emphasis resulting from exclamation points
        # (up to 4 of them)
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        # (empirically derived mean sentiment intensity rating increase for
        # exclamation points)
        ep_amplifier = ep_count * 0.292
        return ep_amplifier

    @staticmethod
    def _amplify_qm(text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # (empirically derived mean sentiment intensity rating increase
                # for question marks)
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier

    @staticmethod
    def _sift_sentiment_scores(sentiments):
        # want separate positive versus negative sentiment scores
        pos_sum = 0.0
        neg_sum = 0.0
        neu_count = 0
        for sentiment_score in sentiments:
            if sentiment_score > 0:
                # compensates for neutral words that are counted as 1
                pos_sum += (float(sentiment_score) + 1)
            if sentiment_score < 0:
                # when used with math.fabs(), compensates for neutrals
                neg_sum += (float(sentiment_score) - 1)
            if sentiment_score == 0:
                neu_count += 1
        return pos_sum, neg_sum, neu_count

    def score_valence(self, sentiments, text):
        """."""
        if sentiments:
            sum_s = float(sum(sentiments))
            # compute and add emphasis from punctuation in text
            punct_emph_amplifier = self._punctuation_emphasis(text)
            if sum_s > 0:
                sum_s += punct_emph_amplifier
            elif sum_s < 0:
                sum_s -= punct_emph_amplifier

            compound = normalize(sum_s)
            # discriminate between pos, neg and neutral sentiment scores
            pos_sum, neg_sum, neu_count = \
                self._sift_sentiment_scores(sentiments)

            if pos_sum > math.fabs(neg_sum):
                pos_sum += punct_emph_amplifier
            elif pos_sum < math.fabs(neg_sum):
                neg_sum -= punct_emph_amplifier

            total = pos_sum + math.fabs(neg_sum) + neu_count
            pos = math.fabs(pos_sum / total)
            neg = math.fabs(neg_sum / total)
            neu = math.fabs(neu_count / total)

        else:
            compound = 0.0
            pos = 0.0
            neg = 0.0
            neu = 0.0

        sentiment_dict = \
            {"neg": round(neg, 3),
             "neu": round(neu, 3),
             "pos": round(pos, 3),
             "compound": round(compound, 4)}

        return sentiment_dict
