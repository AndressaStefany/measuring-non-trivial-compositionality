from collections import namedtuple

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import neptune
from neptunecontrib.api import log_table


from metrics.tre import TreeReconstructionError, LinearComposition, AdditiveComposition, MLPComposition
from protocols import get_negation_ntc_protocol, get_context_sensitive_ntc_protocol, get_order_sensitive_ntc_protocol, \
    get_trivially_compositional_protocol, get_holistic_protocol, get_nontrivially_compositional_protocol, \
    get_diagonal_ntc_protocol

sns.set_style("white")
NUM_COLORS = NUM_SHAPES = 25
NUM_SEEDS = 3
df = pd.DataFrame(columns=['protocol', 'metric', 'value', 'seed'])
neptune.init('tomekkorbak/ntc')
neptune.create_experiment(upload_source_files=['**/*.py*'], properties=dict(num_seeds=NUM_SEEDS, num_colors=NUM_COLORS))
protocol = namedtuple('Protocol', ['protocol_name', 'protocol_obj', 'max_length', 'num_concepts'])
protocols = [
    protocol('negation', get_negation_ntc_protocol(), 4, 11+3),
    protocol('context sensitive', get_context_sensitive_ntc_protocol(NUM_COLORS, NUM_SHAPES), 2, NUM_COLORS+NUM_SHAPES+3),
    protocol('order sensitive', get_order_sensitive_ntc_protocol(NUM_COLORS, NUM_SHAPES), 2, NUM_COLORS+NUM_SHAPES+3),
    protocol('entangled', get_nontrivially_compositional_protocol(NUM_COLORS, NUM_SHAPES), 2, NUM_COLORS+NUM_SHAPES),
    protocol('diagonal', get_diagonal_ntc_protocol(NUM_COLORS, NUM_SHAPES), 2, NUM_COLORS+NUM_SHAPES),
    protocol('TC', get_trivially_compositional_protocol(NUM_COLORS, NUM_SHAPES), 2, NUM_COLORS+NUM_SHAPES),
    protocol('holistic', get_holistic_protocol(NUM_COLORS, NUM_SHAPES), 2, NUM_COLORS+NUM_SHAPES)
]
for seed in range(NUM_SEEDS):
    for protocol_name, protocol_obj, max_length, num_concepts in protocols:
        metrics = {
            'TRE additive': TreeReconstructionError(num_concepts, max_length, AdditiveComposition),
            'TRE linear': TreeReconstructionError(num_concepts, max_length, LinearComposition),
            'TRE nonlinear': TreeReconstructionError(num_concepts, max_length, MLPComposition),
        }
        for metric_name, metric in metrics.items():
            print(protocol_name, metric_name)
            value = metric.measure(protocol_obj)
            df.loc[len(df)] = [protocol_name, metric_name, -value, seed]
log_table('df', df)
df.to_csv('results_2.csv')


with sns.plotting_context('paper', font_scale=1.3):
    all_tre = df[df['protocol'] != 'holistic']
    p = sns.catplot(x='value', y='protocol', col='metric', data=df, kind='box',
                    sharex=True, height=2.5, margin_titles=True)
    p.set_titles(row_template='{row_name}', col_template = '{col_name}')
    p.savefig('figure_1.png', dpi=300)
    neptune.log_image('figure', 'figure_1.png')
