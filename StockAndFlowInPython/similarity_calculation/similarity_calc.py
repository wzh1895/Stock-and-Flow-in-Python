"""
Calculating similarity between two dynamic behaviors (time sequences) using DTW (dynamic time warping)
"""

from dtw import dtw
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# TESTS

test1 = np.array([100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]).reshape(-1, 1)
test2 = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]).reshape(-1, 1)
# ramp from 0 to 100
test3 = np.arange(101).reshape(-1, 1)
# ramp from 100 to 0
test4 = np.linspace(100, 0, 101)
# ramp from 0 to 50
test5 = np.linspace(0, 50, 101)
# ramp from 50 to 0
test6 = np.linspace(50, 0, 101)


class SimilarityCalculator(object):
    def __init__(self):
        pass

    @staticmethod
    def categorize_behavior(who_compare, compare_with='./similarity_calculation/basic_behaviors.csv'):
        """
        Compare reference mode with known typical behavior patterns.
        """
        data = pd.read_csv(compare_with)

        basic_behaviors = dict()
        basic_behaviors["constant"] = np.array(data["Constant"].tolist()).reshape(-1, 1)
        basic_behaviors["growth_a"] = np.array(data["GrowthA"].tolist()).reshape(-1, 1)
        basic_behaviors["growth_b"] = np.array(data["GrowthB"].tolist()).reshape(-1, 1)
        basic_behaviors["growth_c"] = np.array(data["GrowthC"].tolist()).reshape(-1, 1)
        basic_behaviors["growth_d"] = np.array(data["GrowthD"].tolist()).reshape(-1, 1)
        basic_behaviors["decline_a"] = np.array(data["DeclineA"].tolist()).reshape(-1, 1)
        basic_behaviors["decline_b"] = np.array(data["DeclineB"].tolist()).reshape(-1, 1)
        basic_behaviors["decline_c"] = np.array(data["DeclineC"].tolist()).reshape(-1, 1)
        basic_behaviors["decline_d"] = np.array(data["DeclineD"].tolist()).reshape(-1, 1)

        # stretch x0 to a length close to 100.
        # Temporarily only consider len(x0) < 100.
        factor_x = round(100 / len(who_compare))
        x1 = np.kron(who_compare, np.ones((factor_x, 1)))

        # stretch x0 to a height close to 100.
        # Temporarily only consider vertical range of x0 < 100.
        factor_y = 100.0/(who_compare.max() - who_compare.min())
        x = np.array([(i - who_compare.min()) * factor_y for i in x1]).reshape(-1, 1)

        comparison_figure = Figure(figsize=(5, 4))
        comparison_plot = comparison_figure.add_subplot(111)

        distances = {} # distance :basic behavior
        for basic_behavior in basic_behaviors.keys():
            y = basic_behaviors[basic_behavior]
            dist, cost, acc, path = dtw(x, y, dist=lambda x, y: np.linalg.norm(x-y, ord=1))
            distances[dist] = basic_behavior
            # print(basic_behavior, dist)
            comparison_plot.plot(y)

        closest_behavior = distances[min(distances.keys())]
        print("Classified as: ", closest_behavior)

        comparison_plot.plot(x)
        return closest_behavior, comparison_figure

    @staticmethod
    def similarity_calc(who_compare, compare_with):
        # print(who_compare)
        # print(compare_with)
        """
        Compare two behaviors
        :param who_compare:
        :param compare_with:
        :return:
        """
        # stretch x0 to a length close to 100.
        # Temporarily only consider len(x0) < 100.
        factor_x1 = round(100 / len(who_compare))
        x1 = np.kron(who_compare, np.ones((factor_x1, 1)))
        # print('x1', x1)

        # stretch x0 to a height close to 100.
        # Temporarily only consider vertical range of x0 < 100.
        factor_y1 = 100.0 / (who_compare.max() - who_compare.min())
        series_1 = np.array([(i - who_compare.min()) * factor_y1 for i in x1]).reshape(-1, 1)
        # print('series_1', series_1)

        # stretch y0 to a length close to 100.
        # Temporarily only consider len(x0) < 100.
        factor_x2 = round(100 / len(compare_with))
        x2 = np.kron(compare_with, np.ones((factor_x2, 1)))

        # stretch y0 to a height close to 100.
        # Temporarily only consider vertical range of x0 < 100.
        factor_y2 = 100.0 / (compare_with.max() - compare_with.min())
        series_2 = np.array([(i - compare_with.min()) * factor_y2 for i in x2]).reshape(-1, 1)

        comparison_figure = Figure(figsize=(5, 4))
        comparison_plot = comparison_figure.add_subplot(111)

        dist, cost, acc, path = dtw(series_1, series_2, dist=lambda x, y: np.linalg.norm(x - y, ord=1))
        # print(basic_behavior, dist)
        comparison_plot.plot(series_1)
        comparison_plot.plot(series_2)
        print("Distance: {}".format(dist))
        return dist, comparison_figure




if __name__ == '__main__':
    similarity_calculator1 = SimilarityCalculator()
    similarity_calculator1.categorize_behavior(test1)
