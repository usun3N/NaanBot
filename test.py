aaaa = {"a": {"1": "りんご"}}

print(aaaa.get("b", {}).update({"2": "みかん"}))
print(aaaa)