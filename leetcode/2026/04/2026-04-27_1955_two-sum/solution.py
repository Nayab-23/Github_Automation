def twoSum(nums, target):
    seen_nums = {}

    for i in range(len(nums)):
        complement = target - nums[i]
        if complement in seen_nums:
            return [seen_nums[complement], i]
        seen_nums[nums[i]] = i

print(twoSum([2,7,11,15], 9))