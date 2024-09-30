import threading
import time
import numpy as np


def partial_sum(array, start, end, result, index):
    result[index] = sum(array[start:end])


def array_sum_using_threads(array, num_threads):
    size = len(array)
    chunk_size = size // num_threads
    threads = []
    result = [0] * num_threads

    for i in range(num_threads):
        start_index = i * chunk_size
        if i == num_threads - 1:
            end_index = size
        else:
            end_index = start_index + chunk_size

        thread = threading.Thread(target=partial_sum, args=(array, start_index, end_index, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(result)


# Основная часть программы
if __name__ == "__main__":
    array_size = 10 ** 7
    array = np.random.randint(0, 100, size=array_size)

    for num_threads in [1, 2, 4, 8, 16, 32]:
        start = time.time()
        total_sum = array_sum_using_threads(array, num_threads)
        elapsed_time = time.time() - start
        print(f"Сумма: {total_sum}, Время работы с {num_threads} потоками: {elapsed_time:.6f} секунд")
