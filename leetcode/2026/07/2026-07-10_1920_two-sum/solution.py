def two_sum(nums, target):
    for i in range(len(nums)):
        complement = target - nums[i]
        if complement in nums[i+1:] and nums.index(complement) != i:
            return [i, nums.index(complement,i+1)]
print(two_sum([2,7,11,15], 9))