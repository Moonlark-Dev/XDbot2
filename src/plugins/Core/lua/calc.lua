local env = math
env.math = math

function run_sandbox(code)
  local func = load("return " .. code, nil, "t", env)
  if func ~= nil then
    return func()
  end
  return "无法识别的表达式："..code
end
