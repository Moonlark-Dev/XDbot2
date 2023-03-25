local env = {math = math}

function run_sandbox(code)
  local func, _ = load("return " .. code, nil, "t", env)
  if func ~= nil then
    return func()
  end
  return _
end
