from forest_fire import update_grid, calculate_results, save_results_to_db, UNBURNED, BURNING, BURNED
import unittest
from unittest.mock import patch
import numpy as np

class TestForestFireSimulation(unittest.TestCase):

    def setUp(self):
        self.grid_size = 50
        self.T_burn = 3
        self.P_burn = 0.3
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.burn_time = np.zeros((self.grid_size, self.grid_size), dtype=int)

        # Випадкове початкове загоряння
        num_initial_burning = 5
        self.initial_burning_cells = np.random.choice(self.grid_size**2, num_initial_burning, replace=False)
        for cell in self.initial_burning_cells:
            x, y = cell // self.grid_size, cell % self.grid_size
            self.grid[x, y] = BURNING
            self.burn_time[x, y] = self.T_burn
    
    # Тест на оновлення сітки з лісом
    def test_update_grid(self):
        new_grid = update_grid(self.grid, self.burn_time)
        self.assertEqual(new_grid.shape, self.grid.shape)
        self.assertTrue(np.array_equal(new_grid[self.grid == BURNING], np.ones((self.grid == BURNING).sum())))
        self.assertTrue(np.all(np.isin(new_grid, [UNBURNED, BURNING, BURNED])))

    # Тест на обчислення результату
    def test_calculate_results(self):
        burned_cells, burned_ratio = calculate_results(self.grid)
        total_cells = self.grid_size * self.grid_size
        expected_burned_cells = np.count_nonzero(self.grid == BURNED)
        expected_burned_ratio = expected_burned_cells / total_cells
        self.assertEqual(burned_cells, expected_burned_cells)
        self.assertAlmostEqual(burned_ratio, expected_burned_ratio)

    # Тестуємо збереження результатів в базу даних
    def test_save_results_to_db(self):
        P_burn = 0.3
        T_burn = 3
        burned_cells = 1
        burned_ratio = 1 / (self.grid_size * self.grid_size)
        try:
            save_results_to_db(P_burn, T_burn, burned_cells, burned_ratio)
        except Exception as e:
            self.fail(f"save_results_to_db raised an exception {e}")

if __name__ == '__main__':
    unittest.main()
