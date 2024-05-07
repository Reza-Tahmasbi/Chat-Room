import re
# take the length
# message = "Private message, length=<14> to <Asal>,<Reza>:<Hello Everyone>"
message = "Private message, length=<11> to <Asal>,<Reza>:<Hello World>"
message = message.split("to")[1]
message = message.split(":")[0]
result = re.findall(r'<(\w+)>', message)
# result = re.search('<(\w+)>', message).group(1)
print(result)
# print(match.group(1))
# take the user_name
# pattern = r'from (.+) to'
# match = re.search(pattern, message)