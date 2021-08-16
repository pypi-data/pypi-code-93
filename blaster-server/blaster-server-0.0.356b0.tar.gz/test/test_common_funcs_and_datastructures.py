
def test_sanitized_dicts_list():
	from blaster.common_funcs_and_datastructures import SanitizedDict, SanitizedList
	sd = SanitizedDict(a="<a>", b="<b>")
	sd["c"] = "<c>"
	sd["d"] = {"e": "<e>", "f": "<f>"}

	for k, v in sd.items():
		print(k, v)
	for k, v in sd["d"].items():
		print(k, v)

	sl = SanitizedList(["<a>", "<b>"])
	sl.append({"c": "<c>", "d": "<d>"})
	sl.extend(["<e>", "<f>"])
	for i in sl:
		print(i)
	for k, v in sl[2].items():
		print(k, v)






def test():
	test_sanitized_dicts_list()


if __name__ == "__main__":
	test()
