function run_sandbox(code)
  local func, msg = loadstring(code)
  if func ~= nil then
    setfenv(func, {math = math})
    return pcall(func)
  end
  return msg
end

