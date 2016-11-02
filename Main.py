from WordCollection import WordCollection

def main():
    text = ""
    with open("hippogriff.txt") as file:
        for line in file:
            text += line
    wc = WordCollection()
    
    wc.findElements(text)

if __name__ == "__main__":
    main()

