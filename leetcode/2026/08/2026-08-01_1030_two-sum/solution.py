def two_sum(nums, target):
    for i in range(len(nums)):
        if target - nums[i] in nums[i+1:]:
            return [i, nums.index(target - nums[i], i + 1)]

print(two_sum([2, 7, 11, 15], 9))