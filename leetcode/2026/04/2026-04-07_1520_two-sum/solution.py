def two_sum(nums, target):

    for i in range(len(nums)):
        complement = target - nums[i]

        if complement in nums[i+1:] and nums[i+1:].index(complement) > i:
            return [i, nums[i+1:].index(complement) + i + 1]