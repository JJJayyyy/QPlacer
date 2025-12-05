import os
import sys
import warnings
import pickle
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qplacer_bm.collision_check import FreqCollisionChecker
from qplacer_bm import qplacement_database, qplacement_param
sys.modules['qplacement_database'] = qplacement_database
sys.modules['qplacement_param'] = qplacement_param
warnings.filterwarnings("ignore", message=".*is not valid file")


TOPOLOGY = ["grid-25"]
PLACEMENT_LIST = ["wp_wf_03", "classical", "default"]
OUTPUT_FILE = 'device_data.pkl'


def load_testcase(topology, topology_setup_dir, suffix='wp_wf'):
    testcase_name = f"{topology}_{suffix}"
    suffix_dir_path = os.path.join(topology_setup_dir, testcase_name)

    if not os.path.isdir(suffix_dir_path):
        warnings.warn(f"{suffix_dir_path} is not valid directory", UserWarning)
        return None

    print("=================================")
    print(f'Topology: {topology}, Suffix: {suffix}')
    files = os.listdir(suffix_dir_path)
    testcase = defaultdict()

    for cur_file in files:
        file_path = os.path.join(suffix_dir_path, cur_file)
        print(f'    File: {file_path}')
        if file_path.endswith('.log'):
            testcase["log"] = file_path
        elif file_path.endswith(f'{testcase_name}_params.pkl'):
            with open(file_path, 'rb') as f:
                testcase['params'] = pickle.load(f)
        elif file_path.endswith(f'{testcase_name}_db.pkl'):
            with open(file_path, 'rb') as f:
                testcase['db'] = pickle.load(f)

    assert all(value is not None for value in testcase.values()), \
        f"Missing pkl/json files for {topology}/{suffix}"

    testcase["lef"] = testcase['params'].file_paths["lef"]
    testcase["def"] = os.path.join(suffix_dir_path, f"{testcase_name}.gp.def")
    testcase["lg_def"] = os.path.join(suffix_dir_path, f"{testcase_name}.lg.def")

    for file_key in ['lef', 'def', 'lg_def']:
        print(f'{file_key.upper()}: {testcase[file_key]}', end="\t")
        if os.path.isfile(testcase[file_key]):
            print('[OK]')
        else:
            print('[MISSED]')

    return testcase


def analyze_collisions(testcase, suffix):
    collision_checker = FreqCollisionChecker(
        testcase["lg_def"],
        testcase["params"],
        testcase["db"]
    )

    impacted_qubits = collision_checker.plot_collisions(
        verbal=False,
        suffix=f"_{suffix}"
    )

    collision_checker.check_integration(verbal=False)
    edge_collision_map = collision_checker.edge_collision_map
    qubit_adjacency_map = collision_checker.qubit_touch_check(verbal=False)

    print(f'Qubit adjacency map ({len(qubit_adjacency_map)}): {qubit_adjacency_map}')
    print(f'Edge collisions: {len(edge_collision_map)}, {sum(edge_collision_map.values())}')

    poly_area = collision_checker.get_total_area()
    min_bounding_rect = collision_checker.get_min_bounding_rect()
    mbr_area = min_bounding_rect.area
    collision_length = collision_checker.total_collision_length
    hotspot_area = collision_length * int(
        collision_checker.params.partition_size *
        collision_checker.params.scale_factor
    )
    hotspot_pct = hotspot_area / poly_area

    print(f"Poly Area: {poly_area:.4f}, MBR Area: {mbr_area:.4f}, "
          f"Collision len: {collision_length:.4f}, "
          f"Hotspot area: {hotspot_area:.4f}, pct: {hotspot_pct:.4f}")

    return {
        "db": testcase["db"],
        "params": testcase["params"],
        "def_path": testcase["lg_def"],
        "edge_collision_map": edge_collision_map,
        "qubit_adjacency_map": qubit_adjacency_map,
        "poly_area": poly_area,
        "mbr_area": mbr_area,
        "hs_pct": hotspot_pct,
        "impactq": impacted_qubits
    }


def main():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    results = defaultdict(dict)

    for topology in TOPOLOGY:
        for placement_suffix in PLACEMENT_LIST:
            results[topology][placement_suffix] = dict()
            topology_setup_dir = f'results/{topology}'

            testcase = load_testcase(topology, topology_setup_dir, suffix=placement_suffix)
            if testcase is None:
                continue

            print("_________________________________________")
            result_data = analyze_collisions(testcase, placement_suffix)
            results[topology][placement_suffix] = result_data

    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(results, f)
        print(f"\nSaved data to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
