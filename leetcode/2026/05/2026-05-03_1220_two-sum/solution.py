def two_sum(nums, target):
    # Create a dictionary to store the complement of each number
    nums_dict = {}
    for i in range(len(nums)):
        complement = target - nums[i]
        if complement in nums_dict:
            return [nums_dict[complement], i]
        nums_dict[nums[i]] = i
    return []