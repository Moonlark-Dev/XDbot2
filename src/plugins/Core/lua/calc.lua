local loadstring = loadstring or load

function run_sandbox(code)
  local func, msg = loadstring(code)
  setfenv(func, {math = math})
  return func
end
print(run_sandbox([[print(1+1)]]))
