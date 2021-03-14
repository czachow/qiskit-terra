from qiskit.transpiler import PassManager, CouplingMap
from qiskit.transpiler.passes import BasisTranslator
from qiskit.transpiler.passes import UnrollCustomDefinitions
from qiskit.transpiler.passes import Unroll3qOrMore
from qiskit.transpiler.passes import CheckMap
from qiskit.transpiler.passes import BarrierBeforeFinalMeasurements
from qiskit.transpiler.passes import StochasticSwap
from qiskit.transpiler.passes import FullAncillaAllocation
from qiskit.transpiler.passes import EnlargeWithAncilla
from qiskit.transpiler.passes import ApplyLayout
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

def custom_pass_manager(backend, layout_instance, seed=None):
    basis_gates = backend.configuration().basis_gates
    coupling_map = CouplingMap(backend.configuration().coupling_map)

    def _swap_condition(property_set):
        return not property_set['is_swap_mapped']

    _embed = [FullAncillaAllocation(coupling_map), EnlargeWithAncilla(), ApplyLayout()]
    _unroll3q = Unroll3qOrMore()
    _swap_check = CheckMap(coupling_map)
    _swap = [BarrierBeforeFinalMeasurements()]
    _swap += [StochasticSwap(coupling_map, trials=20, seed=seed)]
    _unroll = [UnrollCustomDefinitions(sel, basis_gates), BasisTranslator(sel, basis_gates)]

    pm = PassManager()
    pm.append(layout_instance)
    pm.append(_embed)
    pm.append(_unroll3q)
    pm.append(_swap_check)
    pm.append(_swap, condition=_swap_condition)
    pm.append(_unroll)
    return pm
