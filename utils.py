"""Some language tools for the extraction of semantic head, lemmatization, ..."""
import json
import spacy
import graphviz
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

from collections import defaultdict


class LanguageUtils(object):

    def __init__(self, language):
        self.nlp = spacy.load(language)
        self.lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
    
    def semantic_head(self, text):
        """Extracts the semantic head, as a single word"""
        return str(list(self.nlp(text).sents)[0].root)
    
    def lemmatize(self, word):
        """Returns the lemma from the given words"""
        return self.lemmatizer(word, 'NOUN')
    
    def semantic_head_lemmatize(self, text):
        head = list(self.nlp(text).sents)[0].root
        lemma = head.lemma_
        if lemma == '-PRON-':
            # https://github.com/explosion/spaCy/issues/31
            if head.text in ('I', 'me', 'you', 'he', 'she', 'we', 'us', 'you', 'they', 'them'):
                lemma = 'person'
            elif head.text in ('it'):
                lemma = 'thing'
        return lemma


class HuricUtils(object):

    def __init__(self):
        with open('data/huric_alexa.json') as f:
            content = json.load(f)
        
        self.frame_elements = {}
        for t in content['interactionModel']['languageModel']['types']:
            self.frame_elements[t['name']] = [el['name']['value'] for el in t['values']]

    def get_frame_elements_values(self, frame):
        return self.frame_elements[frame]

class GraphUtils(object):

    def __init__(self):
        pass

    def edges_name_normalize(self, edges_list, clean_name_fn=lambda a: a):
        edges_list = set([(clean_name_fn(a), clean_name_fn(b), label) for (a, b, label) in edges_list])
        return edges_list

    def create_graph(self, edges_list, clean_name_fn=lambda a: a):
        """clean_name_fn is a function that can be passed to retrieve a node name from a uri"""
        graph = graphviz.Digraph('dot') # format='svg' or 'dot'
        nodes_colors = defaultdict(lambda: set())
        for a_uri, b_uri, label in edges_list:
            node_a_color, node_b_color = self.get_node_color(a_uri), self.get_node_color(b_uri)
            a, b = clean_name_fn(a_uri), clean_name_fn(b_uri)
            nodes_colors[a].add(node_a_color)
            nodes_colors[b].add(node_b_color)
            graph.edge(a, b, label)
        
        for node_name, colors in nodes_colors.items():
            if len(colors) > 1:
                color = 'purple'
            else:
                color = colors.pop()
            graph.node(node_name, color=color)
        
        return graph

    def get_node_color(self, node_name):
        if 'dbpedia.org/' in node_name:
            if '/resource/' in node_name:
                return 'red'
            elif '/ontology/' in node_name:
                return 'blue'
        return 'black'

    def get_roots(self, edges_list):
        candidates = defaultdict(lambda: False)
        for a, b, _ in edges_list:
            candidates[b] = True
        for a, b, _ in edges_list:
            candidates[a] = False
        results = [k for k, v in candidates.items() if v]
        return results