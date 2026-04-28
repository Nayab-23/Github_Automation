def two_sum(nums, target):
    # Using a dictionary to store the complement of each number
    complements = {}
    for i, num in enumerate(nums):
        if (target - num) in complements:
            return [complements[target - num], i]
        complements[num] = i