
local env = {math = math}

function run_sandbox(code)
  local func, _ = load("return " .. code, nil, "t", env)
  return func()
end
-- print(run_sandbox("1+1"))
