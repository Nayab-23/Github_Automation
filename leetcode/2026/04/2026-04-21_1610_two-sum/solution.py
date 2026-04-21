def two_sum(nums, target):
    # Create a dictionary to store the complement of each number and its index
    num_to_index = {}

    for i, num in enumerate(nums):
        if (target - num) in num_to_index:
            return [num_to_index[target - num], i]
        num_to_index[num] = i

    return []