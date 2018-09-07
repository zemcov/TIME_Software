def main():
    file = open('tempfiles/stop.txt', 'w')
    file.write('Stop')
    file.close()
    print('Program Stopped')


if __name__ == '__main__':
    main()
