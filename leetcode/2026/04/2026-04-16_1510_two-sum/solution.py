def two_sum(nums, target):
    # Dictionary to store the complement of each number and its index
    complement_dict = {}

    for i, num in enumerate(nums):
        complement = target - num
        if complement in complement_dict:
            return [complement_dict[complement], i]
        else:
            complement_dict[num] = i

    # If no solution is found
    return []