def two_sum(nums, target):
    hash_table = {}
    for i in range(len(nums)):
        complement = target - nums[i]
        if complement in hash_table:
            return [hash_table[complement], i]
        hash_table[nums[i]] = i
    return []