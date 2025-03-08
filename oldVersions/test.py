import numpy as np
import time

# Standard Python list rotation
def rotate_list(arr):
    return [arr[-1]] + arr[:-1]

# NumPy array rotation
def rotate_numpy(arr):
    np_arr = np.array(arr)
    return np.roll(np_arr, 1).tolist()

# Creating a small dataset
arr = list(range(1, 101))

# Timing Python list rotation
start_time = time.time()
for _ in range(10000):
    rotate_list(arr)
python_time = time.time() - start_time

# Timing NumPy array rotation
start_time = time.time()
for _ in range(10000):
    rotate_numpy(arr)
numpy_time = time.time() - start_time

print(f"Python list rotation time: {python_time:.6f} seconds")
print(f"NumPy array rotation time: {numpy_time:.6f} seconds")


from enum import Enum

class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    def is_weekend(self):
        return self in {Weekday.SATURDAY, Weekday.SUNDAY}

# Example usage
day = Weekday.SATURDAY
print(f"Is {day.name} a weekend? {day.is_weekend()}")
