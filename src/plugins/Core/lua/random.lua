local math = math
local random = math.random()
math.randomseed(os.time())

rand = function(Max, Min)
  if Min > Max then
    return random(Max, Min)
  else
    return random(Min, Max)
  end
end
