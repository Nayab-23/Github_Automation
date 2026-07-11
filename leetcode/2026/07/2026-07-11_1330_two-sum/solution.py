def two_sum(nums, target):
    num_dict = {}

    for i in range(len(nums)):
        complement = target - nums[i]
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[nums[i]] = i
    return None