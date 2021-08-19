from cowpy import cow


def run(name="Hello, poetry!"):
    msg = cow.milk_random_cow(name)
    print(msg)


if __name__ == "__main__":
    run()
