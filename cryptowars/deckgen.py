#!/usr/bin/python
import random,string,os

"""
Shamelessly ripped off: 
http://mail.python.org/pipermail/tutor/2001-June/006301.html
"""
def get_rword():
    stat = os.stat('/usr/share/dict/words')
# the filesize if the 7th element of the array
    flen = stat[6]
    f = open('/usr/share/dict/words')
    words = []
    while len(words) < 5:
        # seek to a random offset in the file
        f.seek(int(random.random() * flen))
    # do a single read with sufficient characters
        chars = f.read(50)
    # split it on white space
        wrds = string.split(chars)
        # the first element may be only a partial word so use the second
        # you can also make other tests on the word here
        if len(wrds[1]) > 3 and len(wrds[1]) < 9:
            words.append(wrds[1])
    f.close()
    return random.choice(words)
    
ciphers = ["Vinegere","DES","3DES","TEA","XTEA","RC4","Camellia","Twofish","Blowfish"\
           "AES-CTR 128", "AES-ECB 128", "AES-CBC 128", "AES-CBC 256"]
def create_crypto_card():
    string = "- name: " + get_rword() + "\n"
    ctype = random.choice(['equipment','technology','location','agent'])
    string += "  type: " + ctype + "\n"
    quantity = random.randint(1,4)
    string += "  quantity: " + str(quantity) + "\n"
    string += "  cost: " + str(random.randint(1,150)) + "\n"
    string += "  description: " + get_rword() + "\n"
    string += "  action: " + get_rword() + "\n"
    if (ctype == "agent"):
        string += "  evo: 3" + "\n"
        string += "  cipher: " + random.choice(ciphers) + "\n"
        string += "  intelligence: " + str(random.randint(30,100)) + "\n"
        string += "  infiltration: " + str(random.randint(30,100)) + "\n"        
        string += "  attack: " + str(random.randint(30,100)) + "\n"        
        string += "  defence: " + str(random.randint(30,100)) + "\n"        
        string += "  slots: " + str(random.randint(2,4)) + "\n"
        string += "  training: " + str(random.randint(3,5)) + "\n"
    elif (ctype == "location"):
        string += "  traceability: " + str(random.randint(1,60)) + "\n"        
        string += "  difficulty: " + str(random.randint(1,60)) + "\n"
        string += "  slots: " + str(random.randint(1,4)) + "\n" 
    return string,quantity
    
def main():
    fname = get_rword() + ".deck"
    print "Creating " + fname + "."
    f = open(fname, 'w')
    f.write("name: " + get_rword() + "\n")
    f.write("description: " + get_rword() + "\n")
    f.write("cards: " + "\n")
    quantity = 0
    while (quantity <= 60):
        card,quan = create_crypto_card()
        f.write(card)
        quantity += quan
        
    
if __name__ == "__main__":
        main()
        
