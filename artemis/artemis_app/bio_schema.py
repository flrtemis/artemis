"""BioMetrics factored from pinned neural-sim/metrics.py; no torch import."""
from dataclasses import dataclass,field

@dataclass
class BioMetrics:
    """All bio-side diagnostic values including the extended set."""
    step: int = 0
    synaptic_weight: float = 0.0
    mastery: float = 0.0
    delta: float = 0.0
    dopamine: float = 0.0
    sparsity: float = 0.0
    dendritic_signal: list = field(default_factory=list)
    place_x: list = field(default_factory=list)
    place_y: list = field(default_factory=list)
    place_labels: list = field(default_factory=list)
    active_fraction: float = 0.0
    attention_focus: float = 0.0
    homeostatic_norms: list = field(default_factory=list)
    attractor_variance: float = 0.0
    mean_firing_rate: float = 0.0
    certainty: float = 0.0
    habit_strength: float = 0.0
    plasticity: float = 0.0
    synapse_density: float = 0.0
    bypass_ratios: list = field(default_factory=list)
    cortical_stability: float = 0.0
    wm_profile: list = field(default_factory=list)
    pain_triggered: float = 0.0
    pain_rate: float = 0.0
    memory_retention: float = 0.0
    population_diversity: float = 0.0
    noise_benefit: float = 0.0
    column_differentiation: float = 0.0
    specialisation: list = field(default_factory=list)
    specialisation_entropy: float = 0.0
    neuron_activities: list = field(default_factory=list)
    spike_pairs: list = field(default_factory=list)
    oscillation_bands: dict = field(default_factory=lambda: {'delta': 0.0, 'theta': 0.0, 'alpha': 0.0, 'beta': 0.0, 'gamma': 0.0})
    brain_state: str = 'resting'
    thalamic_input: float = 0.0
    neuromodulator_levels: dict = field(default_factory=lambda: {'dopamine': 0.5, 'acetylcholine': 0.5, 'norepinephrine': 0.5})
    column_sync: list = field(default_factory=list)
    apical_error: float = 0.0
    consolidation_score: float = 0.0
    brain_positions: list = field(default_factory=list)
    spike_arcs: list = field(default_factory=list)
