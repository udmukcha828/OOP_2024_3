from argparse import ArgumentParser
import json
import time
from multiprocessing import Pool, Manager
from utils import Norm, normalize_angle, argmax


def get_cumulative_probability(x: float, y: float, h: float, x_dist: Norm, y_dist: Norm, h_dist: Norm) -> float:
    return x_dist.pdf(x) * y_dist.pdf(y) * h_dist.pdf(h)


def get_transition_probability(p: tuple, q: tuple, delta: tuple, mot_params: dict) -> float:
    dist_l = Norm(mu=mot_params["linear"]["mean"], std=mot_params["linear"]["stddev"])
    dist_a = Norm(mu=mot_params["angular"]["mean"], std=mot_params["angular"]["stddev"])
    s = (delta[0] ** 2 + delta[1] ** 2) ** 0.5
    s_t = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
    if s == 0:
        x = 1
    else:
        p_l = (s_t - s) / s
        x = dist_l.pdf(p_l)
    p_a = normalize_angle(q[2] - p[2] - delta[2])
    y = dist_a.pdf(p_a)
    return x * y


def calculate_probabilities(args):
    index, data_cur, data_prev, delta, mot_params, prev_probs, weight = args
    prob_values = []
    prev_indices = []

    for i, x_c, y_c, h_c, w_c in zip(range(len(data_cur["x"])), data_cur["x"], data_cur["y"], data_cur["heading"],
                                     data_cur["weight"]):
        max_prob = 0
        max_index = -1

        for j, x_p, y_p, h_p in zip(range(len(data_prev["x"])), data_prev["x"], data_prev["y"], data_prev["heading"]):
            tran_prob = get_transition_probability((x_p, y_p, h_p), (x_c, y_c, h_c), delta, mot_params)
            current_prob = w_c * tran_prob * prev_probs[j]
            if current_prob > max_prob:
                max_prob = current_prob
                max_index = j

        prob_values.append(max_prob)
        prev_indices.append(max_index)

    return index, prob_values, prev_indices


if __name__ == "__main__":
    parser = ArgumentParser(description="Generate trajectory with Viterbi algorithm")
    parser.add_argument("graph", help="path to particle transition graph files")
    parser.add_argument("config", help="localization config name")
    parser.add_argument("out", help="path to output file")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)
        x_mu, y_mu = config["initial_position"]
        h_mu = config["initial_heading"]
        x_dist = Norm(mu=x_mu, std=config["init_position_stddev"])
        y_dist = Norm(mu=y_mu, std=config["init_position_stddev"])
        h_dist = Norm(mu=h_mu, std=config["init_heading_stddev"])
        mot_params = config["motion_params"]

    graph = []
    with open(args.graph) as f:
        for line in f:
            graph.append(json.loads(line))

    total_steps = len(graph)
    prev_probs = [1] * len(graph[0]["particles"]["x"])  # начальная вероятность, равная 1
    prev = [[-1] * len(graph[0]["particles"]["x"])]
    prob = [[get_cumulative_probability(x, y, h, x_dist, y_dist, h_dist) * w for x, y, h, w in
             zip(graph[0]["particles"]["x"],
                 graph[0]["particles"]["y"], graph[0]["particles"]["heading"], graph[0]["particles"]["weight"])]]

    start = time.time()

    with Pool() as pool:
        print(start)
        for step in range(1, total_steps):
            print(step)
            print(total_steps)

            data_cur = graph[step]["particles"]
            data_prev = graph[step - 1]["particles"]
            delta_x = graph[step]["delta_odometry"]["position"]["x"]
            delta_y = graph[step]["delta_odometry"]["position"]["y"]
            delta_h = graph[step]["delta_odometry"]["heading"]
            delta = (delta_x, delta_y, delta_h)
            results = pool.map(calculate_probabilities,
                   [(i, data_cur, data_prev, delta, mot_params, prev[step - 1], data_cur["weight"][i])
                    for i in range(len(data_cur["x"]))])

            prob_values = [0] * len(data_cur["x"])
            prev_indices = [-1] * len(data_cur["x"])
            for idx, p_values, p_indices in results:
                prob_values[idx] = p_values
                prev_indices[idx] = p_indices
                prob.append([x / sum(prob_values) for x in prob_values])  # Нормализация вероятностей
                prev.append(prev_indices)
    print(time.time() - start)
    j = argmax(prob[-1])
    idx_path = []
    i = len(graph) - 1
    while j != -1:
        idx_path.append(j)
        j = prev[i][j]
        i -= 1
    trajectory = []
    for i, j in enumerate(idx_path[::-1]):
        trajectory.append((graph[i]["particles"]["x"][j],
                       graph[i]["particles"]["y"][j],
                       graph[i]["particles"]["heading"][j]))

    with open(args.out, "w") as f:
        json.dump(trajectory, f)

