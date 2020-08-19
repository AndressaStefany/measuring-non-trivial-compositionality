from collections import defaultdict
from typing import List

import numpy as np

from metrics.base import Metric
from protocols import Protocol

"""
Adapted from
https://github.com/facebookresearch/EGG/blob/4eca7c0b0908c05d9d402c9c5d20ccf8aaae01b2/egg/zoo/compo_vs_generalization/intervention.py#L45-L92 and
https://github.com/facebookresearch/EGG/blob/4eca7c0b0908c05d9d402c9c5d20ccf8aaae01b2/egg/zoo/language_bottleneck/intervention.py#L14-L61
"""


def compute_entropy(symbols: List[str]) -> float:
    frequency_table = defaultdict(float)
    for symbol in symbols:
        frequency_table[symbol] += 1.0
    H = 0
    for symbol, freq in frequency_table.items():
        p = frequency_table[symbol]/len(symbols)
        H += -p * np.log(p)
    return H / np.log(2)


def compute_mutual_information(concepts: List[str], symbols: List[str]) -> float:
    concept_entropy = compute_entropy(concepts)  # H[p(concepts)]
    symbol_entropy = compute_entropy(symbols)  # H[p(symbols)]
    symbols_and_concepts = [symbol + concept for symbol, concept in zip(symbols, concepts)]
    symbol_concept_joint_entropy = compute_entropy(symbols_and_concepts)  # H[p(concepts, symbols)]
    return concept_entropy + symbol_entropy - symbol_concept_joint_entropy


def get_permutation_invariant_protocol(protocol: Protocol) -> Protocol:
    return {derivation: sorted(message) for derivation, message in protocol.items()}


class Disentanglement(Metric):

    def __init__(self, max_message_length: int, num_concept_slots: int):
        self.max_message_length = max_message_length
        self.num_concept_slots = num_concept_slots
        self.permutation_invariant = False

    def measure(self, protocol: Protocol) -> float:
        if self.permutation_invariant:
            protocol = get_permutation_invariant_protocol(protocol)

        disentanglement_scores = []
        non_constant_positions = 0

        for j in range(self.max_message_length):
            symbols_j = [message[j] for message in protocol.values()]
            symbol_mutual_info = []
            symbol_entropy = compute_entropy(symbols_j)
            for i in range(self.num_concept_slots):
                concepts_i = [derivation[i] for derivation in protocol.keys()]
                mutual_info = compute_mutual_information(concepts_i, symbols_j)
                symbol_mutual_info.append(mutual_info)
            symbol_mutual_info.sort(reverse=True)

            if symbol_entropy > 0:
                disentanglement_score = (symbol_mutual_info[0] - symbol_mutual_info[1]) / symbol_entropy
                disentanglement_scores.append(disentanglement_score)
                non_constant_positions += 1
        return sum(disentanglement_scores)/non_constant_positions


class PositionalDisentanglement(Metric):

    def __init__(self, max_message_length: int, num_concept_slots: int):
        self.max_message_length = max_message_length
        self.num_concept_slots = num_concept_slots
        self.permutation_invariant = False


class BagOfWordsDisentanglement(Metric):

    def __init__(self, max_message_length: int, num_concept_slots: int):
        self.max_message_length = max_message_length
        self.num_concept_slots = num_concept_slots
        self.permutation_invariant = True



