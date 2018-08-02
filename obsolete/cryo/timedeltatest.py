import datetime as d


def main():
    time = d.datetime.utcnow()
    print(time)
    newtime = time - d.timedelta(seconds=10)
    print(newtime)


if __name__ == '__main__':
    main()
