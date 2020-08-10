from bs4 import BeautifulSoup
import requests

def scrap_rollno():
    # url = 'http://192.168.43.94:8000/input.txt'
    url = 'http://192.168.43.94:8000/MFRC522-python-master/input.txt'
    print("Scrapping Rollno ...")
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        data = soup.findAll(text=True)
        # data = str(data)
        if len(data)>1:
            print("Wrong Input")
            return ""
        print("&&&&&&&&", data)
        print("&&&&&&&&", str(data[0]), '&', sep='')
        return str(data[0])
    except requests.exceptions.ConnectionError:
        print("Request exceptions connection error")
        return ""


if __name__ == "__main__":
    rollno = scrap_rollno()
    print(rollno)